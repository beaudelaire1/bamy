import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_homepage_accessible(client):
    """
    Vérifie que la page d'accueil renvoie un statut HTTP 200.
    """
    url = reverse("core:home")
    response = client.get(url)
    assert response.status_code == 200