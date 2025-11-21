from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.detail, name="detail"),
    # Les noms de routes suivants sont préfixés par "cart_" pour éviter
    # toute collision avec d'autres applications lors de l'utilisation de
    # reverse() sans namespace.
    path("add/<int:product_id>/", views.add, name="cart_add"),
    path("update/<int:product_id>/", views.update, name="cart_update"),
    path("remove/<int:product_id>/", views.remove, name="cart_remove"),
    path("clear/", views.clear, name="cart_clear"),
    path("add-legacy/<int:product_id>/", views.add_legacy, name="cart_add_legacy"),

    # Application d'un code promo au panier
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
]
