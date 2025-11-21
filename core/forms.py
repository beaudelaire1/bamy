"""
Forms for the core application.

The ``ContactForm`` allows visitors to send a message to the site
administrator or support team. It collects a name, an email address
and a message. All fields are required by default. Implementing a
contact form directly in the site reduces friction for potential
customers who need assistance and demonstrates professionalism.
"""

from django import forms


class ContactForm(forms.Form):
    """Simple contact form with name, email and message fields."""

    name = forms.CharField(
        max_length=100,
        label="Nom",
        widget=forms.TextInput(attrs={
            "placeholder": "Votre nom",
            "class": "w-full px-3 py-2 border rounded-md",
        }),
    )

    email = forms.EmailField(
        label="Adresse e‑mail",
        widget=forms.EmailInput(attrs={
            "placeholder": "votre@exemple.com",
            "class": "w-full px-3 py-2 border rounded-md",
        }),
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={
            "placeholder": "Comment pouvons‑nous vous aider ?",
            "rows": 6,
            "class": "w-full px-3 py-2 border rounded-md",
        }),
    )