from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class CartAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="api@example.com",
            username="api_user",
            password="password123",
        )

    def test_cart_requires_authentication(self):
        url = reverse("cart-detail-api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
