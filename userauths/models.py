from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    company_name = models.CharField(max_length=255, blank=True, default="")
    # futur: siret, phone, roles, etc.

    #: Indique si ce compte B2B a été vérifié par un administrateur.  Tant que
    #: cette case n'est pas cochée, les tarifs sont masqués et un badge
    #: “Compte en vérification” est affiché sur le site.  Les visiteurs ou
    #: utilisateurs non connectés verront également les prix masqués.
    is_b2b_verified = models.BooleanField(default=False, verbose_name="Compte B2B vérifié")

    def __str__(self):
        return self.username


class Address(models.Model):
    """
    Carnet d’adresses pour un utilisateur.

    Permet de stocker plusieurs adresses (siège, entrepôt, magasin) et de
    sélectionner une adresse par défaut.  Ces adresses peuvent ensuite être
    utilisées lors du checkout ou du passage de commande.
    """

    TYPE_CHOICES = [
        ("HQ", "Siège"),
        ("Warehouse", "Entrepôt"),
        ("Store", "Magasin"),
        ("Other", "Autre"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    company_name = models.CharField("Entreprise", max_length=255, blank=True, default="")
    contact_name = models.CharField("Nom du contact", max_length=255, blank=True, default="")
    address1 = models.CharField("Adresse", max_length=255)
    address2 = models.CharField("Complément", max_length=255, blank=True, default="")
    city = models.CharField("Ville", max_length=100)
    postcode = models.CharField("Code postal", max_length=20)
    country = models.CharField("Pays", max_length=100, default="France")
    phone = models.CharField("Téléphone", max_length=50, blank=True, default="")
    type = models.CharField("Type", max_length=20, choices=TYPE_CHOICES, default="HQ")
    is_default = models.BooleanField("Par défaut", default=False)

    class Meta:
        verbose_name = "adresse"
        verbose_name_plural = "adresses"
        ordering = ["user", "-is_default"]

    def save(self, *args, **kwargs):
        # S'assurer qu'une seule adresse par défaut est définie pour l'utilisateur
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.address1}, {self.city}"


class EmailChangeRequest(models.Model):
    """
    Stocke une demande de changement d'email en attente de validation.

    Lorsqu'un utilisateur souhaite modifier son adresse e‑mail, une entrée
    est créée avec un jeton unique et la nouvelle adresse. Un email de
    confirmation contenant le lien avec ce jeton est envoyé à la nouvelle
    adresse. Lorsque l'utilisateur clique sur le lien, la modification
    est appliquée et la demande est marquée comme utilisée.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_change_requests")
    new_email = models.EmailField()
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "demande de changement d'email"
        verbose_name_plural = "demandes de changement d'email"

    def __str__(self) -> str:
        return f"Changement {self.user} vers {self.new_email}"
