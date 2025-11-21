from django.db import models
from django.conf import settings



class IntegrationLog(models.Model):
    """
    Enregistre les exécutions d'intégration de données.
    Chaque entrée représente un import ou une synchronisation avec un
    service externe. Cela facilite le suivi et le débogage.
    """
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "journal d'intégration"
        verbose_name_plural = "journaux d'intégration"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"


class ImportTask(models.Model):
    """
    Enregistre une tâche d'importation de fichier exécutée de manière
    asynchrone.  Elle permet de suivre l'état d'un import en cours et
    d'afficher un historique des imports réalisés par un utilisateur.

    La clé étrangère ``user`` pointe vers le modèle utilisateur défini dans
    ``AUTH_USER_MODEL``, garantissant la compatibilité avec les comptes
    personnalisés.  Les fichiers importés sont stockés dans le dossier
    ``imports/`` et les statuts possibles sont :

    * ``pending`` – en attente de traitement
    * ``processing`` – en cours d'exécution
    * ``completed`` – terminé avec succès
    * ``failed`` – terminé avec erreurs

    Les champs ``success_count`` et ``failure_count`` résument le nombre
    d'objets créés/mis à jour et d'erreurs rencontrées lors du traitement.
    """

    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Utilisateur ayant lancé la tâche d'import."
    )
    file = models.FileField(upload_to='imports/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    errors = models.TextField(blank=True, null=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "tâche d'importation"
        verbose_name_plural = "tâches d'importation"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Import #{self.id} - {self.get_status_display()}"