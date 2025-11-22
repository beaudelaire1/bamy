from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .models import Customer, QuoteRequest
from .forms import ContactForm, QuoteRequestForm


@login_required
def customer_list(request):
    """
    Affiche la liste des clients.

    Cette vue simple permet aux utilisateurs authentifiés de consulter
    l'ensemble des clients enregistrés dans la base CRM. À terme, on
    pourrait ajouter de la pagination et des filtres par statut.
    """
    customers = Customer.objects.all()
    return render(request, "crm/customer_list.html", {"customers": customers})


def contact_view(request):
    """
    Formulaire de contact pour les prospects et clients professionnels.

    Lors de la soumission, un accusé de réception est envoyé au client
    reprenant son message, et une notification interne est envoyée à la
    liste `INTERNAL_CONTACTS`.  Le sujet interne est préfixé par la
    catégorie sélectionnée (par ex. « [CONTACT:pricing] »).
    """
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Construction du sujet interne
            subject_key = data.get("subject") or "other"
            subject_internal = f"[CONTACT:{subject_key}] Nouveau message"
            # Corps du mail interne
            internal_body = (
                f"Société: {data['company']}\n"
                f"Nom: {data.get('first_name','')} {data.get('last_name','')}\n"
                f"Email: {data['email']}\n"
                f"Téléphone: {data.get('phone','')}\n"
                f"Sujet: {dict(form.fields['subject'].choices).get(subject_key, subject_key)}\n\n"
                f"Message:\n{data['message']}"
            )
            # Corps du mail pour l'expéditeur
            client_body = (
                "Bonjour,\n\n"
                "Nous avons bien reçu votre demande de contact et vous remercions de l'intérêt que vous portez à nos services. "
                "Voici un récapitulatif de votre message :\n\n"
                f"Sujet : {dict(form.fields['subject'].choices).get(subject_key, subject_key)}\n"
                f"Message :\n{data['message']}\n\n"
                "Notre équipe vous répondra dans les meilleurs délais.\n\n"
                "Cordialement,\nL'équipe Xeros"
            )
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None
            # Envoi des emails
            try:
                send_mail(subject_internal, internal_body, from_email, getattr(settings, "INTERNAL_CONTACTS", []))
                send_mail(
                    "Votre demande de contact Xeros", client_body, from_email, [data["email"]]
                )
            except Exception:
                # On ignore les exceptions d'envoi en mode dev (console backend)
                pass
            # Crée une notification pour l'utilisateur connecté le cas échéant
            if request.user.is_authenticated:
                try:
                    from notifications.models import Notification  # type: ignore
                    Notification.objects.create(
                        user=request.user,
                        message="Votre demande de contact a été envoyée avec succès."
                    )
                except Exception:
                    pass
            messages.success(request, "Votre message a été envoyé. Merci de nous avoir contactés.")
            return redirect("crm:contact")
    else:
        form = ContactForm()
    context = {
        "form": form,
        # Clé de site reCAPTCHA v3/v2 Invisible pour injection dans le template. Si non défini, le formulaire
        # n'injectera pas de script. La clé publique est utilisée côté client.
        "recaptcha_site_key": getattr(settings, "RECAPTCHA_PUBLIC_KEY", None),
    }
    return render(request, "crm/contact.html", context)


def quote_request_view(request):
    """
    Formulaire pour les demandes de devis.

    Les références et quantités sont saisies sous forme de texte libre (une
    référence et quantité par ligne).  À la validation, la demande est
    enregistrée en base de données et un email est envoyé au client ainsi
    qu'à l'équipe interne.  Les utilisateurs connectés verront leurs
    coordonnées pré-remplies.
    """
    initial = {}
    if request.user.is_authenticated:
        u = request.user
        initial = {
            "email": getattr(u, "email", ""),
            "first_name": getattr(u, "first_name", ""),
            "last_name": getattr(u, "last_name", ""),
            "company": getattr(u, "company_name", ""),
        }
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            qr = QuoteRequest.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=data["email"],
                company=data.get("company", ""),
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                phone=data.get("phone", ""),
                items="\n".join(data["items"]),
                comment=data.get("comment", ""),
            )
            # Email interne
            subject_internal = f"[DEVIS] Demande #{qr.pk}"
            internal_body = (
                f"Demande de devis #{qr.pk}\n"
                f"Date: {qr.created_at}\n"
                f"Société: {qr.company}\n"
                f"Nom: {qr.first_name} {qr.last_name}\n"
                f"Email: {qr.email}\n"
                f"Téléphone: {qr.phone}\n\n"
                f"Références:\n{qr.items}\n\n"
                f"Commentaire:\n{qr.comment}"
            )
            client_body = (
                "Bonjour,\n\n"
                "Nous avons bien reçu votre demande de devis. Voici un récapitulatif de votre demande :\n\n"
                f"Références demandées :\n{qr.items}\n\n"
                f"Commentaire :\n{qr.comment}\n\n"
                "Notre équipe reviendra vers vous rapidement avec une proposition.\n\n"
                "Cordialement,\nL'équipe Xeros"
            )
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None
            try:
                send_mail(subject_internal, internal_body, from_email, getattr(settings, "INTERNAL_CONTACTS", []))
                send_mail(
                    "Votre demande de devis Xeros", client_body, from_email, [qr.email]
                )
            except Exception:
                pass
            # Crée une notification pour l'utilisateur connecté le cas échéant
            if request.user.is_authenticated:
                try:
                    from notifications.models import Notification  # type: ignore
                    Notification.objects.create(
                        user=request.user,
                        message=f"Votre demande de devis #{qr.pk} a été envoyée."
                    )
                except Exception:
                    pass
            messages.success(request, "Votre demande de devis a été envoyée.")
            return redirect("crm:quote_request")
    else:
        form = QuoteRequestForm(initial=initial)
        # Préremplir le champ items à partir du paramètre GET product
        product_id = request.GET.get("product")
        if product_id:
            try:
                from catalog.models import Product  # import local pour éviter dépendance circulaire
                prod = Product.objects.get(pk=int(product_id))
                form.initial.setdefault(
                    "items",
                    f"{prod.sku or prod.id}: {prod.min_order_qty}",
                )
            except Exception:
                pass
    context = {
        "form": form,
        "recaptcha_site_key": getattr(settings, "RECAPTCHA_PUBLIC_KEY", None),
    }
    return render(request, "crm/quote_request.html", context)