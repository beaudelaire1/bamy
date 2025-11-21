"""Vues pour soumettre des demandes de retours."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import OrderItem
from .models import ReturnRequest


@login_required
def request_return(request, item_id: int):
    """Crée une demande de retour pour un article de commande.

    L'utilisateur doit être propriétaire de la commande pour créer
    cette demande. Un motif est requis pour motiver le retour.
    """
    item = get_object_or_404(OrderItem, pk=item_id, order__user=request.user)
    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        if reason:
            ReturnRequest.objects.create(order_item=item, reason=reason)
            messages.success(request, "Votre demande de retour a été soumise.")
        else:
            messages.error(request, "Merci de renseigner un motif pour le retour.")
        return redirect("orders:success", order_number=item.order.order_number)
    # GET : afficher un formulaire simple
    return render(request, "returns/request_return.html", {"item": item})