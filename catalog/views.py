from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Brand
from django.db import models
from cart.forms import AddToCartForm

from decimal import Decimal
from urllib.parse import urlencode

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Min, Max
from django.db.models.functions import Coalesce
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

# Les imports ci‑dessus incluent déjà la fonction ``render`` et les modèles nécessaires.
# Les doublons de ``render`` et ``Product`` ont été supprimés pour éviter toute confusion.
from .forms import CatalogFilterForm

# Ajout import pour les avis
from reviews.forms import ReviewForm
from django.db.models import Avg

@vary_on_cookie
@cache_page(60 * 10)  # mise en cache de 10 minutes pour optimiser les performances, variation par cookie pour éviter les fuites de session
def product_list(request):
    """
    Liste produits avec filtres: Catégorie, Marque, Prix min/max.
    - Le tri s'applique sur le prix effectif (discount_price sinon price) ou sur la récence.
    - Les bornes min/max de prix sont calculées APRES filtre Catégorie/Marque, AVANT filtre prix.
    """
    base_qs = Product.objects.filter(is_active=True).select_related("brand", "category")
    eff = Coalesce("discount_price", "price")

    form = CatalogFilterForm(request.GET or None)

    # 1) on applique d'abord Catégorie/Marque pour calculer des bornes pertinentes
    filtered_for_bounds = base_qs
    if form.is_valid():
        cat = form.cleaned_data.get("category")
        br = form.cleaned_data.get("brand")
        if cat:
            filtered_for_bounds = filtered_for_bounds.filter(category=cat)
        if br:
            filtered_for_bounds = filtered_for_bounds.filter(brand=br)

    bounds = filtered_for_bounds.annotate(effective_price=eff).aggregate(
        db_min=Min("effective_price"),
        db_max=Max("effective_price"),
    )
    db_min = bounds["db_min"] or Decimal("0.00")
    db_max = bounds["db_max"] or Decimal("0.00")

    # 2) queryset final = on réapplique Catégorie/Marque + Prix + Recherche
    qs = filtered_for_bounds
    if form.is_valid():
        a = form.cleaned_data.get("min_price")
        b = form.cleaned_data.get("max_price")
        q = form.cleaned_data.get("query")
        if a is not None:
            qs = qs.annotate(effective_price=eff).filter(effective_price__gte=a)
        if b is not None:
            qs = qs.annotate(effective_price=eff).filter(effective_price__lte=b)
        # Recherche textuelle : nom, code article ou EAN
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(article_code__icontains=q)
                | Q(ean__icontains=q)
            )

    # Tri
    sort = request.GET.get("sort", "")
    if sort == "price_asc":
        qs = qs.annotate(effective_price=eff).order_by("effective_price", "-updated_at")
    elif sort == "price_desc":
        qs = qs.annotate(effective_price=eff).order_by("-effective_price", "-updated_at")
    elif sort == "recent":
        qs = qs.order_by("-updated_at")
    else:
        qs = qs.order_by("-updated_at")

    # Pagination
    paginator = Paginator(qs, 24)
    page = request.GET.get("page", 1)
    try:
        products = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        products = paginator.page(1)

    # Querystring sans 'page' pour la pagination
    params = request.GET.copy()
    params.pop("page", None)
    qstring = urlencode(params, doseq=True)

    ctx = {
        "products": products,
        "form": form,
        "price_min_db": db_min,
        "price_max_db": db_max,
        "current_sort": sort,
        "qstring": qstring,
    }
    return render(request, "catalog/product_list.html", ctx)
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(is_active=True, category__in=[category] + list(category.children.all()))
    context = {
        "category": category,
        "products": products.select_related("brand", "category"),
    }
    return render(request, "catalog/category.html", context)

def brand_view(request, slug):
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(is_active=True, brand=brand).select_related("brand", "category")
    return render(request, "catalog/brand.html", {"brand": brand, "products": products})

def product_detail(request, slug):
    """
    Affiche la fiche produit détaillée.

    Cette vue récupère un produit actif par son slug et passe au template
    une instance de formulaire ``AddToCartForm`` pour permettre l'ajout
    direct au panier depuis la fiche. En cas d'inactivité du produit,
    ``get_object_or_404`` lèvera une 404.
    """
    product = get_object_or_404(
        Product.objects.select_related("brand", "category"),
        slug=slug,
        is_active=True,
    )
    # Récupère les avis et la note moyenne
    product_reviews = product.reviews.select_related("user").all()
    avg_rating = product_reviews.aggregate(avg=Avg("rating")).get("avg") or 0
    ctx = {
        "product": product,
        "cart_form": AddToCartForm(),
        "reviews": product_reviews,
        "avg_rating": avg_rating,
        "review_form": ReviewForm(),
    }
    return render(
        request,
        "catalog/product_detail.html",
        ctx,
    )


def week_selection(request):
    """
    Affiche la liste des produits sélectionnés de la semaine.

    Les produits sont marqués via le champ booléen ``is_week_selection`` et
    peuvent être liés à une période (date de début/fin). On filtre
    uniquement les produits actifs dont la date courante est comprise
    entre ``selection_start`` et ``selection_end`` lorsque ces champs sont
    renseignés.
    
    Les règles d'affichage des prix (gating B2B) sont gérées dans le
    template. On passe simplement la liste des produits au contexte.
    """
    from datetime import date

    today = date.today()
    qs = Product.objects.filter(is_active=True, is_week_selection=True)
    qs = qs.filter(
        models.Q(selection_start__isnull=True) | models.Q(selection_start__lte=today),
        models.Q(selection_end__isnull=True) | models.Q(selection_end__gte=today),
    ).select_related("brand", "category")
    context = {
        "products": qs,
    }
    return render(request, "catalog/week_selection.html", context)
