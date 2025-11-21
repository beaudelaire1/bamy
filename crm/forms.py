"""Formulaires pour l'application CRM.

Ce module définit les formulaires utilisés pour le contact grossiste et la
demande de devis.  Les champs reflètent les exigences du cahier de
charges : société, nom/prénom, email, téléphone, sujet et message pour
le formulaire de contact, et références/quantités accompagnées d'un
commentaire pour la demande de devis.  Les validations minimales
sont effectuées par Django.
"""

from django import forms
from django.conf import settings

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # peut être None en environnement restreint


def verify_recaptcha(token: str, secret_key: str) -> bool:
    """
    Vérifie le jeton reCAPTCHA côté serveur en appelant l'API Google.

    Si l'API ``requests`` n'est pas disponible ou qu'une erreur se produit,
    la fonction retourne ``True`` afin de ne pas bloquer l'utilisateur en
    environnement de développement. En production, la validation stricte
    est requise.

    :param token: jeton renvoyé par grecaptcha.execute côté client
    :param secret_key: clé secrète fournie par Google reCAPTCHA
    :return: booléen indiquant si le jeton est valide
    """
    if not token or not secret_key:
        return False
    if requests is None:
        # Pas de bibliothèque requests, on suppose valide pour éviter les blocages
        return True
    try:
        resp = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret_key, "response": token},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            return bool(data.get("success"))
    except Exception:
        # Ne pas lever d'exception en dev ; en production, lever ou logger
        return True
    return False


class ContactForm(forms.Form):
    SUBJECT_CHOICES = [
        ("account", "Ouverture de compte pro"),
        ("pricing", "Conditions tarifaires & RFA"),
        ("supply", "Approvisionnement & Logistique"),
        ("quality", "Qualité & SAV"),
        ("marketing", "Marketing & TG"),
        ("partnership", "Partenariats marque"),
        ("other", "Autre"),
    ]

    company = forms.CharField(label="Société", max_length=255, required=True)
    first_name = forms.CharField(label="Prénom", max_length=100, required=False)
    last_name = forms.CharField(label="Nom", max_length=100, required=False)
    email = forms.EmailField(label="Email", required=True)
    phone = forms.CharField(label="Téléphone", max_length=50, required=False)
    subject = forms.ChoiceField(label="Sujet", choices=SUBJECT_CHOICES, required=True)
    message = forms.CharField(label="Message", widget=forms.Textarea, required=True)

    # Jeton de vérification reCAPTCHA envoyé via un champ caché (invisible).
    captcha_token = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_message(self):
        # Petite normalisation du message : suppression d'espaces superflus
        msg = self.cleaned_data["message"].strip()
        return msg

    def clean(self):
        cleaned = super().clean()
        # Vérifie le reCAPTCHA uniquement si une clé privée est définie en settings
        secret_key = getattr(settings, "RECAPTCHA_PRIVATE_KEY", None)
        if secret_key:
            token = cleaned.get("captcha_token")
            # En cas d'absence de jeton, on déclenche une erreur
            if not token or not verify_recaptcha(token, secret_key):
                raise forms.ValidationError(
                    "La vérification anti‑robot a échoué. Veuillez réessayer."
                )
        return cleaned


class QuoteRequestForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    company = forms.CharField(label="Société", max_length=255, required=False)
    first_name = forms.CharField(label="Prénom", max_length=100, required=False)
    last_name = forms.CharField(label="Nom", max_length=100, required=False)
    phone = forms.CharField(label="Téléphone", max_length=50, required=False)
    items = forms.CharField(
        label="Références et quantités",
        widget=forms.Textarea,
        help_text="Indiquez les références et les quantités souhaitées, une par ligne.",
        required=True,
    )
    comment = forms.CharField(
        label="Commentaire", widget=forms.Textarea, required=False
    )

    # Jeton de vérification reCAPTCHA envoyé via un champ caché (invisible).
    captcha_token = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_items(self):
        data = self.cleaned_data["items"]
        # Normalise le séparateur de lignes et supprime les lignes vides
        lines = [ln.strip() for ln in data.splitlines() if ln.strip()]
        if not lines:
            raise forms.ValidationError("Veuillez saisir au moins une référence.")
        return lines

    def clean(self):
        cleaned = super().clean()
        secret_key = getattr(settings, "RECAPTCHA_PRIVATE_KEY", None)
        if secret_key:
            token = cleaned.get("captcha_token")
            if not token or not verify_recaptcha(token, secret_key):
                raise forms.ValidationError(
                    "La vérification anti‑robot a échoué. Veuillez réessayer."
                )
        return cleaned