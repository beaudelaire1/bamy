from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from core.factory import get_cart_service


class CartServiceTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            username="test_user",
            password="password123",
        )

    def test_get_cart_for_anonymous_user(self):


        request = self.factory.get("/")
        request.user = self.user

        # Ajouter une session (important pour Cart)
        request.session = SessionStore()
        request.session.save()

        service = get_cart_service()
        cart = service.get_cart(request)

