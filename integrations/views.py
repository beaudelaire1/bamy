

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ImportForm
from .models import ImportTask
from .tasks import process_import_task

try:
    # ``kombu`` lève une erreur opérationnelle si le broker est inaccessible.
    from kombu.exceptions import OperationalError as KombuOperationalError
except Exception:
    # fallback silencieux si kombu n'est pas importable
    KombuOperationalError = Exception


@login_required
def import_data(request):
    """Page permettant de lancer un import de produits.

    Si la requête est POST et que le formulaire est valide, une
    :class:`ImportTask` est enregistrée puis traitée de manière
    asynchrone par Celery. Un message de confirmation est affiché et
    l'utilisateur est redirigé vers la page de suivi de cette tâche.
    Sinon, le formulaire vide est rendu avec l'historique des dix
    dernières tâches de l'utilisateur.
    """
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_task = form.save(commit=False)
            import_task.user = request.user
            import_task.save()
            # Tente de déclencher le traitement asynchrone via Celery.
            # Si aucun broker n'est disponible, exécute la tâche de manière synchrone.
            try:
                process_import_task.delay(import_task.id)
            except (KombuOperationalError, ConnectionError):
                process_import_task(import_task.id)
            messages.success(
                request,
                f"Import #{import_task.id} créé avec succès. Traitement en cours."
            )
            return redirect('integrations:import_status', task_id=import_task.id)
    else:
        form = ImportForm()
    tasks = ImportTask.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'integration/import.html', {'form': form, 'tasks': tasks})


@login_required
def import_status(request, task_id):
    """Affiche l'état d'une tâche d'importation.

    Cette vue ne permet d'afficher que les tâches appartenant à
    l'utilisateur courant. Elle montre un récapitulatif du nombre de
    créations/mises à jour et, le cas échéant, détaille les erreurs.
    """
    task = get_object_or_404(ImportTask, id=task_id, user=request.user)
    return render(request, 'integration/import_status.html', {'task': task})
