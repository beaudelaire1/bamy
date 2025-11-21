from __future__ import annotations
from typing import List
from django.shortcuts import render
from django.http import HttpRequest
from .models import Product
from django.contrib.auth.decorators import login_required


def _parse_ids(request: HttpRequest) -> List[int]:
    """
    Supporte:
      - ?ids=1,2,3
      - ?ids[]=1&ids[]=2&ids[]=3
    Nettoie et limite à 100 IDs.
    """
    ids_param = request.GET.get("ids", "")
    many = request.GET.getlist("ids[]")  # si appel sous forme d'array
    tokens: List[str] = []

    if many:
        tokens = many
    elif ids_param:
        tokens = ids_param.split(",")

    out: List[int] = []
    for tok in tokens:
        tok = tok.strip()
        if tok.isdigit():
            out.append(int(tok))
        if len(out) >= 100:
            break
    return out




@login_required
def wishlist_detail(request: HttpRequest):
    ids = _parse_ids(request)

    products = []
    missing_count = 0
    if ids:
        # On ne filtre PAS par is_active pour éviter les faux négatifs.
        qs = Product.objects.filter(id__in=ids).select_related("brand", "category")
        found = list(qs)
        order = {pid: idx for idx, pid in enumerate(ids)}
        # Préserve l'ordre reçu
        products = sorted(found, key=lambda p: order.get(p.id, 10**9))
        missing_count = len(ids) - len(found)

    ctx = {
        "products": products,
        "count": len(products),
        "ids_query": ",".join(map(str, ids)) if ids else "",
        "missing_count": missing_count,
    }
    return render(request, "catalog/wishlist.html", ctx)
