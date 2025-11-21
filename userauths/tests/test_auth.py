from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthFlowTests(TestCase):
    def test_register_login_flow(self):
        r = self.client.get(reverse("userauths:register"))
        self.assertEqual(r.status_code, 200)

        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password1": "Strongpass123!",
            "password2": "Strongpass123!",
            "company_name": "AliceCo",
        }
        r = self.client.post(reverse("userauths:register"), data, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(User.objects.filter(username="alice").exists())

        # Déconnexion puis login
        self.client.get(reverse("userauths:logout"))
        r = self.client.post(reverse("userauths:login"), {"username": "alice", "password": "Strongpass123!"}, follow=True)
        self.assertEqual(r.status_code, 200)
