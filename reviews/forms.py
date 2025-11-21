from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Formulaire pour la création d'un avis.

    Propose une sélection de notes de 1 à 5 et un champ texte pour
    commenter le produit. Les commentaires sont optionnels.
    """

    rating = forms.TypedChoiceField(
        label="Note",
        coerce=int,
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Votre avis"}),
        }