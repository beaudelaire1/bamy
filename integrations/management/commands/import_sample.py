from django.core.management.base import BaseCommand
from integrations.models import IntegrationLog


class Command(BaseCommand):
    help = "Importe des données d'exemple pour le catalogue."

    def handle(self, *args, **options):
        """
        Exécute l'import des données exemples.

        Ce script est volontairement simple. Dans un projet réel,
        il parcourrait un fichier CSV, YAML ou JSON afin de créer
        dynamiquement des objets en base (produits, clients, etc.).
        Pour l'instant, il se contente de consigner une entrée de log.
        """
        log = IntegrationLog.objects.create(
            name="sample_import",
            status="success",
            details="Aucune donnée d'exemple fournie."
        )
        self.stdout.write(self.style.SUCCESS("Import des données d'exemple terminé."))