"""
Client governance and RBAC service.

This module centralises the access control logic associated with
multi‑client support.  Given a Django user and a client instance,
``ClientAccessService`` exposes helpers to determine whether the
user can view catalogues, see promotions, place orders and whether
they are the owner of the client.
"""

from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model

from .models import Client, UserClientLink


class ClientAccessService:
    """Provides high‑level permission checks for client operations."""

    @staticmethod
    def _get_link(user: Optional[get_user_model()], client: Client) -> Optional[UserClientLink]:
        """Return the link between a user and a client, if it exists.

        The method performs a simple lookup on ``UserClientLink`` and
        returns ``None`` if either the user is anonymous or no active
        relationship exists.
        """
        if user is None or not getattr(user, "is_authenticated", False):
            return None
        try:
            return UserClientLink.objects.get(user=user, client=client, is_active=True)
        except UserClientLink.DoesNotExist:
            return None

    @classmethod
    def is_owner(cls, user, client: Client) -> bool:
        """Check if the given user is the owner of the specified client."""
        link = cls._get_link(user, client)
        return bool(link and link.role == UserClientLink.Roles.OWNER)

    @classmethod
    def can_view_catalog(cls, user, client: Client) -> bool:
        """Whether the user can view the client's catalogue.

        Currently any active link grants read access.
        """
        link = cls._get_link(user, client)
        return bool(link)

    @classmethod
    def can_view_promotions(cls, user, client: Client) -> bool:
        """Whether the user can view promotions for the client.

        Promotions may be a gated feature; we check both the link and
        the client's allowed_features list.
        """
        link = cls._get_link(user, client)
        if not link:
            return False
        return "promotions" in (client.allowed_features or []) or cls.is_owner(user, client)

    @classmethod
    def can_order(cls, user, client: Client) -> bool:
        """Whether the user can place orders on behalf of the client.

        Owners and admins can always order.  Members can order by default,
        while read_only users cannot.
        """
        link = cls._get_link(user, client)
        if not link:
            return False
        return link.role in {
            UserClientLink.Roles.OWNER,
            UserClientLink.Roles.ADMIN,
            UserClientLink.Roles.MEMBER,
        }
