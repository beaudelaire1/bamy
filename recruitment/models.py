"""Modèles pour l'application de recrutement.

Cette application gère les offres d'emploi publiées sur le site ainsi
que les candidatures associées. Chaque offre est représentée par un
objet :class:`JobPosting`, et chaque candidature par un objet
:class:`JobApplication` lié à une offre donnée.
"""

from django.db import models
from django.urls import reverse


class JobPosting(models.Model):
    """Représente une offre d'emploi publiée sur le site.

    Les champs de base incluent un titre, un slug pour les URLs, une
    description riche, un lieu, un département ou service et une date de
    publication. Le champ ``is_active`` permet de masquer une offre sans
    la supprimer. Les objets sont ordonnés par date de publication
    décroissante.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    published_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "offre d'emploi"
        verbose_name_plural = "offres d'emploi"
        ordering = ["-published_at"]

    def __str__(self) -> str:  # pragma: no cover
        return self.title

    def get_absolute_url(self) -> str:  # pragma: no cover
        return reverse("recruitment:job_detail", args=[self.slug])


class JobApplication(models.Model):
    """Stocke une candidature soumise pour une offre d'emploi.

    Une candidature est liée à une :class:`JobPosting` et contient les
    coordonnées du candidat, un message et éventuellement un CV (fichier).
    L'horodatage ``created_at`` permet de trier les candidatures par
    ordre d'arrivée.
    """

    job = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    name = models.CharField("Nom", max_length=100)
    email = models.EmailField("E‑mail")
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    message = models.TextField("Message")
    created_at = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(
        "CV", upload_to="applications/resumes/", blank=True, null=True
    )

    # Pièce jointe supplémentaire pour la lettre de motivation.
    cover_letter = models.FileField(
        "Lettre de motivation", upload_to="applications/cover_letters/", blank=True, null=True
    )

    class Meta:
        verbose_name = "candidature"
        verbose_name_plural = "candidatures"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} - {self.job.title}"