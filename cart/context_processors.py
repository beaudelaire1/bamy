from .cart import Cart

def cart(request):
    c = Cart(request)
    return {"cart_count": len(c), "cart_total": c.total}
