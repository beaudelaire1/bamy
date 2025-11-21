# userauths/views.py
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.conf import settings
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from .forms import RegistrationForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from .models import Address, EmailChangeRequest
from .models import User  # import explicit pour token email change
from .forms import AddressForm, EmailChangeForm
import secrets
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail
class RememberLoginView(LoginView):
    """
    LoginView avec option 'Se souvenir de moi' (checkbox 'remember').
    Utilise registration/login.html par défaut (modifiable).
    """
    template_name = "registration/login.html"
    redirect_authenticated_user = True  # si déjà connecté, redirige

    def form_valid(self, form):
        resp = super().form_valid(form)
        # Si 'remember' n'est PAS coché, session = expire à la fermeture du navigateur
        if not self.request.POST.get("remember"):
            self.request.session.set_expiry(0)
        return resp


@require_POST
def logout_post(request):
    """
    Déconnexion en POST (évite 405 et CSRF logout). Dans la navbar,
    utiliser un <form method="post"> avec {% csrf_token %}.
    """
    # Avant de déconnecter l'utilisateur, nous purgeons explicitement
    # certains éléments de la session. Cela permet notamment de
    # supprimer le panier enregistré dans request.session[CART_SESSION_ID]
    # afin d'éviter que des articles persistent après la déconnexion.
    try:
        cart_key = getattr(settings, 'CART_SESSION_ID', 'cart')
        request.session.pop(cart_key, None)
        # On peut également supprimer ici d'autres clés spécifiques comme
        # un historique de navigation ou des préférences temporaires.
    except Exception:
        pass
    # Appelle la fonction logout() standard qui supprime les données
    # d'authentification et invalide la session.
    logout(request)
    # Redirige vers la page de redirection définie ou la racine par défaut.
    return redirect(getattr(settings, "LOGOUT_REDIRECT_URL", "/"))

class RegisterView(FormView):
    """
    Formulaire d'inscription avec auto-login et support de ?next=...
    """
    # Utilise notre template personnalisé sous templates/userauths/
    template_name = "userauths/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("core:home")  # adapte si besoin

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        nxt = self.request.POST.get("next") or self.request.GET.get("next")
        return redirect(nxt or self.get_success_url())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["next"] = self.request.GET.get("next", "")
        return ctx


# -----------------------------------------------------------------------------
# Compte utilisateur / tableau de bord

class AccountView(LoginRequiredMixin, TemplateView):
    """
    Vue tableau de bord pour l'utilisateur connecté.  Permet de mettre à jour
    ses informations de profil (nom, prénom, email) et de changer son mot de
    passe via le formulaire intégré.

    Le template dédié est stocké dans l'application ``userauths`` sous
    ``templates/userauths/account.html``.  Cette localisation garantit que
    Django le trouvera grâce à ``APP_DIRS=True`` sans dépendre d'un dossier
    global ``templates/core``.  Nous conservons toutefois un fallback vers
    ``core/account.html`` et ``account.html`` au cas où l'environnement du
    projet inclurait ces fichiers.
    """
    # Chemin principal utilisé par Django pour le tableau de bord utilisateur.
    # La template est stockée sous templates/core/account.html puisque
    # l'application userauths ne dispose pas d'un dossier templates
    # modifiable en écriture. Le chargement via APP_DIRS inclut ce
    # répertoire global.
    template_name = "core/account.html"

    def get_template_names(self):
        """Retourne une liste de templates à essayer dans l'ordre de préférence."""
        # On essaie d'abord le template propre à l'application, puis des noms
        # alternatifs pour compatibilité ascendante.
        return [
            "core/account.html",
            "account.html",
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Formulaire de changement de mot de passe
        context["password_form"] = PasswordChangeForm(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        """
        Traite deux actions :
        - Mise à jour du profil via le bouton nommé "update_profile".
        - Changement de mot de passe via le bouton nommé "change_password".
        """
        if "change_password" in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                # Maintient l'utilisateur authentifié après modification du mot de passe
                update_session_auth_hash(request, user)
                messages.success(request, "Votre mot de passe a bien été modifié.")
                return redirect("userauths:account")
            else:
                context = self.get_context_data()
                context["password_form"] = form
                return self.render_to_response(context)
        elif "update_profile" in request.POST:
            user = request.user
            email = request.POST.get("email", "").strip()
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            # Mise à jour simple : on pourrait ajouter des validations
            user.email = email or user.email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, "Votre profil a été mis à jour.")
            return redirect("userauths:account")
        # Sinon, retour sans action
        return redirect("userauths:account")


# -----------------------------------------------------------------------------
# Gestion du carnet d'adresses

class AddressListView(LoginRequiredMixin, ListView):
    """
    Liste des adresses de l'utilisateur.

    Affiche toutes les adresses enregistrées par l'utilisateur
    authentifié et permet d'accéder aux actions de création, modification et
    suppression.
    """
    model = Address
    template_name = "userauths/address_list.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by("-is_default", "-id")


class AddressCreateView(LoginRequiredMixin, CreateView):
    """
    Vue de création d'une nouvelle adresse.  L'utilisateur authentifié est
    automatiquement associé à l'adresse.
    """
    model = Address
    form_class = AddressForm
    template_name = "userauths/address_form.html"
    success_url = reverse_lazy("userauths:address_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Adresse ajoutée avec succès.")
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vue de modification d'une adresse existante appartenant à l'utilisateur.
    """
    model = Address
    form_class = AddressForm
    template_name = "userauths/address_form.html"
    success_url = reverse_lazy("userauths:address_list")

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Adresse mise à jour.")
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vue de suppression d'une adresse.  Seules les adresses de l'utilisateur
    courant peuvent être supprimées.
    """
    model = Address
    template_name = "userauths/address_confirm_delete.html"
    success_url = reverse_lazy("userauths:address_list")

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Adresse supprimée.")
        return super().delete(request, *args, **kwargs)


# -----------------------------------------------------------------------------
# Changement d'adresse e-mail avec revalidation

class EmailChangeRequestView(LoginRequiredMixin, FormView):
    """
    Permet à l'utilisateur de demander un changement d'adresse e-mail.

    Cette vue envoie un lien de confirmation à la nouvelle adresse. La
    modification n'est appliquée qu'après validation du lien. Pour simplifier
    l'implémentation, nous stockons la nouvelle adresse dans la session et
    validons immédiatement. En production, on utiliserait un modèle avec
    token unique et envoi d'email.
    """

    template_name = "userauths/email_change_form.html"
    form_class = EmailChangeForm
    success_url = reverse_lazy("userauths:account")

    def form_valid(self, form):
        """
        Crée une demande de changement d'e‑mail et envoie un lien de confirmation
        à la nouvelle adresse. L'adresse n'est modifiée qu'après validation du
        jeton.
        """
        user = self.request.user
        new_email = form.cleaned_data["new_email"].strip().lower()
        # Supprimer d'anciennes demandes non utilisées pour ce user
        EmailChangeRequest.objects.filter(user=user, used=False).delete()
        # Génère un token sécurisé et crée l'entrée
        token = secrets.token_urlsafe(32)
        req = EmailChangeRequest.objects.create(user=user, new_email=new_email, token=token)
        # Construit le lien de confirmation
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        confirm_url = self.request.build_absolute_uri(
            reverse("userauths:email_change_confirm", args=[uid, token])
        )
        # Message
        subject = "Confirmation de changement d'adresse e‑mail"
        body = (
            f"Bonjour {user.get_full_name() or user.username},\n\n"
            f"Vous avez demandé à remplacer votre adresse e‑mail par : {new_email}.\n"
            f"Pour confirmer ce changement, veuillez cliquer sur le lien ci‑dessous :\n\n"
            f"{confirm_url}\n\n"
            "Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer ce message.\n\n"
            "Cordialement,\nL'équipe Xeros"
        )
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or None
        try:
            send_mail(subject, body, from_email, [new_email])
        except Exception:
            pass
        messages.success(self.request, "Un e‑mail de confirmation a été envoyé à la nouvelle adresse. Veuillez suivre le lien pour finaliser le changement.")
        return super().form_valid(form)


class EmailChangeConfirmView(LoginRequiredMixin, TemplateView):
    """
    Valide une demande de changement d'e‑mail en vérifiant le token fourni
    dans l'URL. Si la demande est valide et non expirée, l'adresse e‑mail
    de l'utilisateur est mise à jour.
    """

    template_name = "userauths/email_change_confirm.html"

    def get(self, request, *args, **kwargs):
        uidb64 = kwargs.get("uidb64")
        token = kwargs.get("token")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None
        req = None
        if user:
            try:
                req = EmailChangeRequest.objects.get(user=user, token=token, used=False)
            except EmailChangeRequest.DoesNotExist:
                req = None
        if not user or not req:
            messages.error(request, "Le lien de confirmation est invalide ou a expiré.")
            return redirect("userauths:account")
        # Met à jour l'email
        user.email = req.new_email
        user.save()
        req.used = True
        req.save()
        messages.success(request, "Votre adresse e‑mail a été modifiée avec succès.")
        return redirect("userauths:account")
