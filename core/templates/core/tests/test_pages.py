from django.test import TestCase
from django.urls import reverse

class CorePagesTests(TestCase):
    def test_home_ok(self):
        r = self.client.get(reverse("core:home"))
        self.assertEqual(r.status_code, 200)

    def test_about_ok(self):
        r = self.client.get(reverse("core:about"))
        self.assertEqual(r.status_code, 200)
