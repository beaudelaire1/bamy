from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_title", "product_sku", "unit_price", "quantity", "line_total")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "email", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "email", "first_name", "last_name", "company")
    readonly_fields = ("order_number", "subtotal", "shipping", "total", "created_at")
    inlines = [OrderItemInline]

    # -------------------------------------------------------------------------
    # Actions personnalisées
    #
    # Le cahier des charges prévoit la possibilité, depuis le tableau de
    # bord d'administration, de modifier rapidement l'état d'une commande.
    # Notamment, marquer une commande comme « Payée » lorsqu'un paiement
    # externe (Stripe/PayPal) a été capturé avec succès.  Cette action
    # s'applique en masse depuis la liste des commandes.  Les autres
    # statuts (annulée, remboursée) peuvent être ajoutés au besoin.
    @admin.action(description="Marquer les commandes sélectionnées comme payées")
    def mark_paid(self, request, queryset):
        """
        Définit le statut 'paid' sur toutes les commandes sélectionnées.

        Après captation du paiement via PayPal ou Stripe, l'administrateur
        peut sélectionner les commandes concernées dans l'interface Django
        et déclencher cette action pour mettre à jour leur statut.  Un
        message de confirmation indique combien de commandes ont été mises
        à jour.
        """
        updated = queryset.update(status="paid")
        self.message_user(
            request,
            f"{updated} commande(s) ont été marquées comme payées.",
        )

    actions = [mark_paid]
