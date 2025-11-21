"""
Migration initiale pour l'application ``core``.

Cette migration crée la table ``core_sitesettings`` qui stocke les
informations de branding et de configuration globale du site.  Elle
reprend la définition du modèle ``SiteSettings`` situé dans
``core/models.py``.  Les champs incluent le nom, le slogan, le logo
ainsi que les couleurs principales du thème.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(
                    max_length=100,
                    default="BamyTest",
                    verbose_name="Nom de l'entreprise",
                    help_text="Nom public affiché dans la barre de navigation et le pied de page.",
                )),
                ("tagline", models.CharField(
                    max_length=200,
                    blank=True,
                    verbose_name="Slogan",
                    help_text="Brève description ou tagline de l'entreprise.",
                )),
                ("logo", models.ImageField(
                    upload_to="branding/logos/",
                    blank=True,
                    null=True,
                    verbose_name="Logo",
                    help_text="Logo de l'entreprise affiché dans le header.",
                )),
                ("primary_color", models.CharField(
                    max_length=7,
                    default="#0905f5",
                    verbose_name="Couleur primaire",
                    help_text="Couleur principale utilisée dans le thème (hexadécimale).",
                )),
                ("accent_color", models.CharField(
                    max_length=7,
                    default="#D4AF37",
                    verbose_name="Couleur d'accent",
                    help_text="Couleur d'accent pour les boutons et liens (hexadécimale).",
                )),
                ("dark_color", models.CharField(
                    max_length=7,
                    default="#2D2D2D",
                    verbose_name="Couleur sombre",
                    help_text="Couleur sombre pour l'arrière-plan (hexadécimale).",
                )),
                ("light_color", models.CharField(
                    max_length=7,
                    default="#F8F9FA",
                    verbose_name="Couleur claire",
                    help_text="Couleur claire pour les surfaces et le texte (hexadécimale).",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Créé le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")),
            ],
            options={
                "verbose_name": "configuration du site",
                "verbose_name_plural": "configurations du site",
            },
        ),
    ]