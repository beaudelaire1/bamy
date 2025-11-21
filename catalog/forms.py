from django import forms
from .models import Brand, Category


class CatalogFilterForm(forms.Form):
    """
    Filtre catalogue : catégorie, marque, prix min/max.
    - Tous les champs sont facultatifs (GET).
    - Validation: min_price <= max_price si les deux sont renseignés.
    """
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True).order_by("name"),
        required=False,
        label="Catégorie",
        empty_label="Toutes les catégories",
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True).order_by("name"),
        required=False,
        label="Marque",
        empty_label="Toutes les marques",
    )
    min_price = forms.DecimalField(
        required=False, min_value=0, max_digits=12, decimal_places=2, localize=True,
        label="Min (€)"
    )
    max_price = forms.DecimalField(
        required=False, min_value=0, max_digits=12, decimal_places=2, localize=True,
        label="Max (€)"
    )

    # Champ de recherche libre. Permet de rechercher un produit par
    # désignation, code article ou code EAN. La recherche n'est pas
    # sensible à la casse. Ce champ est facultatif.
    query = forms.CharField(
        required=False,
        max_length=255,
        label="Recherche",
        widget=forms.TextInput(attrs={"placeholder": "Nom, code article ou EAN"}),
    )

    def clean(self):
        cleaned = super().clean()
        a = cleaned.get("min_price")
        b = cleaned.get("max_price")
        if a is not None and b is not None and a > b:
            self.add_error("max_price", "Le prix max doit être ≥ au prix min.")
        return cleaned
