from __future__ import annotations

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


class LoginAPIView(TokenObtainPairView):
    """
    Endpoint JWT standard pour obtenir un couple (access, refresh).
    """

    # On peut personnaliser le serializer plus tard si besoin.
    pass


class RefreshTokenAPIView(TokenRefreshView):
    """
    Endpoint pour rafraîchir le token d'accès.
    """

    pass
