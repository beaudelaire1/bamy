"""
Forms for the integrations app.

This module defines a form used to submit an import task.  It is a
``ModelForm`` bound to the :class:`~integrations.models.ImportTask`
model and restricts the uploaded file to supported formats.  By
default the management command can import CSV, JSON and Excel files,
so the form accepts extensions ``.csv``, ``.tsv``, ``.json``, ``.xls``
and ``.xlsx``.  Additional validation (such as file size checks) can
be added here if necessary.
"""

from django import forms

from .models import ImportTask


class ImportForm(forms.ModelForm):
    """Formulaire pour soumettre une nouvelle tâche d'importation.

    Le fichier transmis doit être au format CSV, TSV, JSON ou Excel.  La
    validation se fait uniquement sur l'extension ; le contenu sera
    examiné lors du traitement asynchrone.  Si vous souhaitez restreindre
    davantage les types de fichiers, modifiez la liste ``allowed_exts``.
    """

    class Meta:
        model = ImportTask
        fields = ['file']

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        # Extensions de fichiers autorisées (en minuscules)
        allowed_exts = {'.csv', '.tsv', '.json', '.xls', '.xlsx'}
        name_lower = uploaded.name.lower()
        if not any(name_lower.endswith(ext) for ext in allowed_exts):
            raise forms.ValidationError(
                "Formats pris en charge : CSV, TSV, JSON, XLS, XLSX."
            )
        return uploaded