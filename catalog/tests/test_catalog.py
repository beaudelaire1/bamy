from django.test import TestCase
from django.urls import reverse
from catalog.models import Category, Brand, Product

class CatalogSmokeTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Lessive")
        self.brand = Brand.objects.create(name="X-Tra")
        self.p = Product.objects.create(
            title="Bouteille 2L",
            sku="XT-2L",
            category=self.cat,
            brand=self.brand,
            price=9.99,
            stock=10,
        )

    def test_list_page(self):
        r = self.client.get(reverse("catalog:product_list"))
        self.assertContains(r, "Bouteille 2L")

    def test_detail_page(self):
        r = self.client.get(self.p.get_absolute_url())
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Bouteille 2L")
