from django.urls import path
from . import views, views_wishlist

app_name = "catalog"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("wishlist/", views_wishlist.wishlist_detail, name="wishlist"),
    path("c/<slug:slug>/", views.category_view, name="category"),
    path("b/<slug:slug>/", views.brand_view, name="brand"),
    path("p/<slug:slug>/", views.product_detail, name="product_detail"),
    # Sélection de la semaine
    path("selection-semaine/", views.week_selection, name="week_selection"),
]
