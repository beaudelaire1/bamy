"""
Définition des URL de l'application d'intégrations.

Ces routes exposent une interface pour lancer un import de données
et consulter son avancement.  L'app utilise ``app_name = 'integration'``
afin de construire des espaces de noms cohérents avec les templates.
"""

from django.urls import path

from . import views

# Nom d'application et espace de noms.  Nous utilisons « integrations » pour
# correspondre au namespace défini dans le routeur principal.
app_name = 'integrations'

urlpatterns = [
    path('import/', views.import_data, name='import_data'),
    path('import/<int:task_id>/', views.import_status, name='import_status'),
]