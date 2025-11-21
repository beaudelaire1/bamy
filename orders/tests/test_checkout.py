from django.test import TestCase
from django.urls import reverse
from catalog.models import Category, Brand, Product

class CheckoutFlowTests(TestCase):
    def setUp(self):
        c = Category.objects.create(name="Lessive")
        b = Brand.objects.create(name="X-Tra")
        self.p = Product.objects.create(title="Bouteille 2L", sku="XT-2L", category=c, brand=b, price=9.99, stock=10)

    def test_checkout_creates_order(self):
        # Ajout au panier
        self.client.post(reverse("cart:cart_add", args=[self.p.id]), {"quantity": 2, "override": False})
        # Checkout
        payload = {
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Durand",
            "phone": "0600000000",
            "company": "AliceCo",
            "address1": "1 rue du Test",
            "address2": "",
            "city": "Cayenne",
            "postcode": "97300",
            "country": "France",
            "notes": "",
        }
        r = self.client.post(reverse("orders:checkout"), payload, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Merci pour votre commande")
