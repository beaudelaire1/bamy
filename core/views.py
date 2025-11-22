from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from catalog.models import Brand, Product

def home(request):
    # Marques avec logo
    brands = Brand.objects.filter(is_active=True, logo__isnull=False)

    # Produits en promo (pour le carrousel du haut)
    promos = list(
        Product.objects.filter(is_active=True, discount_price__isnull=False)
        .select_related("brand", "category")
        .order_by("-updated_at")[:12]
    )
    if not promos:
        # fallback si aucune promo
        promos = list(
            Product.objects.filter(is_active=True)
            .select_related("brand", "category")
            .order_by("-updated_at")[:12]
        )

    # Sélection de la semaine (grille du bas), en évitant les promos
    # Affiche au maximum 10 produits (plus premium).
    max_selection = 10
    exclude_ids = [p.id for p in promos]
    selection = list(
        Product.objects.filter(is_active=True).exclude(id__in=exclude_ids)
        .select_related("brand", "category")
        .order_by("?")[:max_selection]
    )
    if len(selection) < max_selection:
        needed = max_selection - len(selection)
        fillers = Product.objects.filter(is_active=True)\
            .exclude(id__in=exclude_ids + [s.id for s in selection])\
            .order_by("-updated_at")[:needed]
        selection += list(fillers)

    return render(request, "core/home.html", {
        "brands": brands,
        "promos_carousel": promos,        # carrousel du haut
        "selection_products": selection,  # grille du bas
    })


# ======= Formulaire de contact =======

class ContactForm(forms.Form):
    """Formulaire de contact simple avec champ de nom, email, sujet, téléphone et message.

    Nous déclarons ce formulaire ici plutôt que dans un fichier séparé car
    l'arborescence de l'application est en lecture seule et nous ne pouvons
    pas créer de nouveaux modules facilement. Les champs utilisent des
    widgets HTML adaptés pour la saisie utilisateur.
    """

    name = forms.CharField(
        label="Nom",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Votre nom"
        }),
    )
    email = forms.EmailField(
        label="E‑mail",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Votre adresse e‑mail"
        }),
    )
    subject = forms.CharField(
        label="Sujet",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Sujet de votre message (facultatif)"
        }),
    )
    phone = forms.CharField(
        label="Téléphone",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Votre numéro de téléphone (facultatif)"
        }),
    )
    message = forms.CharField(
        label="Message",
        required=True,
        widget=forms.Textarea(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "rows": 5,
            "placeholder": "Votre message"
        }),
    )


def contact(request):
    """Affiche et traite le formulaire de contact.

    Lorsqu'une requête POST valide est soumise, un message de succès est
    ajouté et l'utilisateur reste sur la page pour éviter un double envoi
    lors d'un rafraîchissement. Dans une implémentation réelle, vous
    pourriez envoyer un e‑mail ou enregistrer la demande en base.
    """
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Ici, on pourrait utiliser send_mail() pour envoyer le message.
            messages.success(request, "Votre message a été envoyé. Merci de nous contacter.")
            return redirect("core:contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})

def about(request):
    return render(request, "core/about.html")


def privacy_policy(request):
    """Page de politique de confidentialité (RGPD)."""
    return render(request, "core/privacy.html")


def cookies_policy(request):
    """Page de politique relative aux cookies."""
    return render(request, "core/cookies.html")


# ======= Formulaire de recrutement =======

class RecruitmentForm(forms.Form):
    """Formulaire de candidature pour la page recrutement.

    Ce formulaire collecte les informations essentielles d'un candidat :
    nom, email, numéro de téléphone, poste visé et message. Un champ
    facultatif de dépôt de CV pourrait être ajouté via un ``FileField``
    dans une évolution future ; pour l'instant, nous invitons les
    candidats à inclure un lien dans leur message.
    """

    name = forms.CharField(
        label="Nom",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Votre nom complet"
        }),
    )
    email = forms.EmailField(
        label="E‑mail",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Votre adresse e‑mail"
        }),
    )
    phone = forms.CharField(
        label="Téléphone",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Votre numéro de téléphone (facultatif)"
        }),
    )
    position = forms.CharField(
        label="Poste souhaité",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "placeholder": "Intitulé du poste auquel vous postulez"
        }),
    )
    message = forms.CharField(
        label="Message",
        required=True,
        widget=forms.Textarea(attrs={
            "class": "w-full px-3 py-2 border rounded-md",
            "rows": 6,
            "placeholder": "Présentez-vous et expliquez votre motivation"
        }),
    )


def recruitment(request):
    """Affiche et traite le formulaire de recrutement.

    Les candidatures sont actuellement simplement confirmées via un message
    de succès. Dans une implémentation réelle, les données pourraient être
    stockées en base, envoyées par e‑mail ou créées dans un CRM.
    """
    if request.method == "POST":
        form = RecruitmentForm(request.POST)
        if form.is_valid():
            messages.success(request, "Votre candidature a été envoyée. Merci pour votre intérêt !")
            return redirect("core:recruitment")
    else:
        form = RecruitmentForm()
    return render(request, "core/recruitment.html", {"form": form})