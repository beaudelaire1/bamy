from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Notification


@login_required
def notification_list(request):
    """
    Affiche les notifications de l'utilisateur connecté.
    Les notifications non lues peuvent être mises en évidence dans le template.
    """
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "notifications/list.html", {"notifications": notifications})