from django.test import TestCase
from django.urls import reverse
from catalog.models import Category, Brand, Product

class CartFlowTests(TestCase):
    def setUp(self):
        self.c = Category.objects.create(name="Lessive")
        self.b = Brand.objects.create(name="X-Tra")
        self.p = Product.objects.create(
            title="Bouteille 2L", sku="XT-2L", category=self.c, brand=self.b, price=9.99, stock=10
        )

    def test_add_and_remove(self):
        r = self.client.post(reverse("cart:cart_add", args=[self.p.id]), {"quantity": 2, "override": False}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Bouteille 2L")
        self.assertContains(r, "19.98")  # 2 * 9.99

        r = self.client.get(reverse("cart:cart_remove", args=[self.p.id]), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Bouteille 2L")
