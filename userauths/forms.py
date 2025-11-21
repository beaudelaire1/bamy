# userauths/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

# Importation explicite du modèle Address pour éviter les problèmes
# liés à la récupération du modèle via le champ reverse. La relation
# ``User._meta.get_field('addresses')`` n'existe pas au niveau du Meta
# car il s'agit d'un gestionnaire reverse et non d'un champ.  Nous
# utilisons donc l'import direct du modèle pour construire nos formulaires.
from .models import Address

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Adresse e-mail", required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "w-full border rounded-xl px-3 py-2")


class AddressForm(forms.ModelForm):
    """
    Formulaire CRUD pour la création ou modification d'une adresse.

    Utilise le modèle ``Address`` défini dans ``userauths.models``. Les
    champs sont rendus avec des classes Tailwind pour une meilleure
    intégration visuelle. Le champ ``is_default`` est optionnel mais
    permet à l'utilisateur de choisir l'adresse principale.
    """

    class Meta:
        model = Address
        exclude = ("user",)  # l'utilisateur est fixé dans la vue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "w-full border rounded-xl px-3 py-2 mb-3")
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.setdefault("class", "")


class EmailChangeForm(forms.Form):
    """
    Formulaire pour demander un changement d'adresse email.

    L'utilisateur saisit la nouvelle adresse email. Après validation,
    un lien de confirmation doit être envoyé à cette adresse pour
    valider définitivement la modification.
    """

    new_email = forms.EmailField(label="Nouvelle adresse e-mail", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "w-full border rounded-xl px-3 py-2")

    def clean_new_email(self):
        email = self.cleaned_data["new_email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé par un autre compte.")
        return email
