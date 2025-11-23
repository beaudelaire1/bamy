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


# -----------------------------------------------------------------------------
# BrandingConfig
#
# Ce modèle stocke la configuration de la charte graphique de la boutique B2B.
# Chaque champ est obligatoire afin de garantir que les couleurs primaires et
# secondaires, la police personnalisée et les médias (logo, favicon) soient
# toujours définis.  Une seule instance est généralement nécessaire ; elle
# sera chargée via le context processor ``branding``.  Les couleurs sont
# définies au format hexadécimal (#RRGGBB).
class BrandingConfig(models.Model):
    primary_color = models.CharField(
        max_length=7,
        verbose_name="Couleur principale",
        help_text="Couleur principale du thème (hexadécimal)",
    )
    secondary_color = models.CharField(
        max_length=7,
        verbose_name="Couleur secondaire",
        help_text="Couleur secondaire du thème (hexadécimal)",
    )
    font_url = models.URLField(
        verbose_name="URL de la police",
        help_text="Lien vers la police personnalisée à charger (Google Fonts par ex.)",
        blank=True,
        null=True,
    )
    logo = models.ImageField(
        upload_to="branding/logos/",
        verbose_name="Logo",
        help_text="Logo de la marque utilisé dans l'interface",
        blank=True,
        null=True,
    )
    favicon = models.ImageField(
        upload_to="branding/favicons/",
        verbose_name="Favicon",
        help_text="Icône utilisée dans l'onglet du navigateur",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "configuration de la marque"
        verbose_name_plural = "configurations de la marque"

    def __str__(self) -> str:
        return "Branding configuration"
