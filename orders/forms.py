from django import forms

class CheckoutForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=30, required=False)
    company = forms.CharField(max_length=255, required=False)

    address1 = forms.CharField(max_length=255)
    address2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100)
    postcode = forms.CharField(max_length=20)
    country = forms.CharField(max_length=60, initial="France")

    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
