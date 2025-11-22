"""Formulaires pour l'application de recrutement.

Le formulaire principal permet aux candidats de postuler à une offre
d'emploi. Il s'appuie sur un modèle pour simplifier la création et la
validation des champs.
"""

from django import forms
from .models import JobApplication


class JobApplicationForm(forms.ModelForm):
    """Formulaire de candidature lié au modèle :class:`JobApplication`.

    Les widgets sont personnalisés pour être compatibles avec la
    charte graphique existante (classes Tailwind). Le champ ``resume``
    permet de joindre un fichier, mais son téléchargement dépendra de
    la configuration du stockage dans Django (MEDIA_ROOT et MEDIA_URL).
    """

    class Meta:
        model = JobApplication
        fields = ["name", "email", "phone", "message", "resume"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border rounded-md",
                    "placeholder": "Votre nom",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-3 py-2 border rounded-md",
                    "placeholder": "Votre adresse e‑mail",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border rounded-md",
                    "placeholder": "Votre numéro de téléphone (facultatif)",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border rounded-md",
                    "rows": 6,
                    "placeholder": "Votre message",
                }
            ),
        }