"""Ajout des champs de prix par type de client sur Product.

Cette migration introduit trois nouveaux champs optionnels sur le modèle
Product afin de stocker des tarifs distincts pour les grossistes,
les clients de grande distribution et les petites distributions.  Ces
champs permettent d'importer des fichiers contenant des prix
différenciés et d'afficher des tarifs adaptés directement sans
calcul de remise.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0012_alter_product_article_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="price_wholesaler",
            field=models.DecimalField(
                verbose_name="Prix grossiste",
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                help_text="Tarif appliqué aux clients de type grossiste s'il est renseigné.",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price_big_retail",
            field=models.DecimalField(
                verbose_name="Prix grande distribution",
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                help_text="Tarif appliqué aux clients de type grande distribution (hypermarchés).",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price_small_retail",
            field=models.DecimalField(
                verbose_name="Prix petite distribution",
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                help_text="Tarif appliqué aux clients de type petite distribution ou commerce de proximité.",
            ),
        ),
    ]