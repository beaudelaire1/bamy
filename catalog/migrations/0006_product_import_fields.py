"""
Migration pour ajouter des champs de correspondance aux produits.

Cette migration introduit trois champs au modèle ``Product`` afin de
faciliter l'importation de produits depuis des sources externes :

* ``article_code`` : identifiant unique fourni par le grossiste.
* ``ean`` : code-barres européen (facultatif).
* ``pcb_code`` : code constructeur/PCB (facultatif).

Ces champs sont ajoutés sans valeurs par défaut. Lors d'un import,
vous pourrez renseigner ces attributs pour chaque produit afin de
garder une trace des références d'origine.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0005_product_min_order_qty_product_order_in_packs_and_more"),
    ]

    operations = [
        # On ajoute d'abord le champ sans contrainte d'unicité ni valeur
        # par défaut, afin d'éviter un conflit lors de la migration
        # pour les enregistrements existants. Un champ nul est
        # acceptable provisoirement.
        migrations.AddField(
            model_name="product",
            name="article_code",
            field=models.CharField(
                verbose_name="Code article",
                max_length=64,
                blank=True,
                null=True,
                help_text="Identifiant unique du produit fourni par le grossiste.",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="ean",
            field=models.CharField(
                verbose_name="EAN",
                max_length=14,
                blank=True,
                null=True,
                help_text="Code-barres international du produit.",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="pcb_code",
            field=models.CharField(
                verbose_name="Code PCB",
                max_length=64,
                blank=True,
                null=True,
                help_text="Référence constructeur (PCB) pour le produit.",
            ),
        ),
        # Copie du champ SKU vers article_code pour les enregistrements existants
        migrations.RunPython(
            code=lambda apps, schema_editor: copy_sku_to_article_code(apps, schema_editor),
            reverse_code=migrations.RunPython.noop,
        ),
        # Une fois les données copiées, on applique les contraintes finales
        migrations.AlterField(
            model_name="product",
            name="article_code",
            field=models.CharField(
                verbose_name="Code article",
                max_length=64,
                unique=True,
                help_text="Identifiant unique du produit fourni par le grossiste.",
            ),
        ),
    ]

# Fonctions utilitaires pour cette migration
def copy_sku_to_article_code(apps, schema_editor):
    """
    Pour toutes les entrées existantes, copie le champ ``sku`` dans
    ``article_code``. Cette étape est nécessaire avant d'ajouter la
    contrainte d'unicité sur ``article_code``.

    On utilise l'API ``apps.get_model`` afin de récupérer la classe
    historique du modèle ``Product`` au moment de la migration.
    """
    Product = apps.get_model("catalog", "Product")
    for product in Product.objects.all():
        # Si le champ article_code est vide, on recopie le SKU.
        # S'il existe déjà, on ne l'écrase pas (import préalable).
        if not product.article_code:
            product.article_code = product.sku
            product.save(update_fields=["article_code"])