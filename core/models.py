from django.db import models

class SiteSettings(models.Model):
    """
    Configuration globale de la plateforme.

    Ce modèle permet de personnaliser dynamiquement le nom de l’entreprise,
    son slogan, le logo et les couleurs principales du thème.  Une entrée
    active sera chargée automatiquement via le context processor
    ``core.context_processors.brand`` pour alimenter les templates.  Si
    aucune instance n’est présente en base, les valeurs par défaut
    définies dans ``settings.py`` seront utilisées.
    """

    name = models.CharField(
        max_length=100,
        default="BamyTest",
        verbose_name="Nom de l'entreprise",
        help_text="Nom public affiché dans la barre de navigation et le pied de page.",
    )
    tagline = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Slogan",
        help_text="Brève description ou tagline de l'entreprise.",
    )
    logo = models.ImageField(
        upload_to="branding/logos/",
        blank=True,
        null=True,
        verbose_name="Logo",
        help_text="Logo de l'entreprise affiché dans le header.",
    )
    primary_color = models.CharField(
        max_length=7,
        default="#0905f5",
        verbose_name="Couleur primaire",
        help_text="Couleur principale utilisée dans le thème (hexadécimale).",
    )
    accent_color = models.CharField(
        max_length=7,
        default="#D4AF37",
        verbose_name="Couleur d'accent",
        help_text="Couleur d'accent pour les boutons et liens (hexadécimale).",
    )
    dark_color = models.CharField(
        max_length=7,
        default="#2D2D2D",
        verbose_name="Couleur sombre",
        help_text="Couleur sombre pour l'arrière-plan (hexadécimale).",
    )
    light_color = models.CharField(
        max_length=7,
        default="#F8F9FA",
        verbose_name="Couleur claire",
        help_text="Couleur claire pour les surfaces et le texte (hexadécimale).",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "configuration du site"
        verbose_name_plural = "configurations du site"

    def __str__(self) -> str:
        return self.name
