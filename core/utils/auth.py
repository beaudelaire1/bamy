"""
Helpers around authentication and client context determination.

The B2B context of an authenticated user may determine which pricing
rules apply.  In order to decouple the domain services from the
structure of the user model and its related profile, this module
provides a single function ``get_current_client`` which extracts the
client context (such as ``client_type`` or ``pricing_mode``) from a
Django ``User`` instance.  Services can call this helper to
construct the appropriate ``UserDTO`` without needing to know where
client information is stored.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class CurrentClient:
    """A simple data holder for client context."""

    client_type: Optional[str]
    pricing_mode: Optional[str]


def get_current_client(user: Any) -> CurrentClient:
    """Return the client context for a given user.

    The function inspects the user and its related profile to determine
    the ``client_type`` and ``pricing_mode``.  If no explicit
    ``pricing_mode`` is found it falls back to ``client_type``.

    :param user: A Django ``User`` instance or an object with similar attributes
    :returns: A ``CurrentClient`` describing the pricing context
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return CurrentClient(client_type=None, pricing_mode=None)
    # Extract client_type either from the user or its profile
    client_type = getattr(user, "client_type", None)
    # pricing_mode may be defined on the profile or directly on the user
    pricing_mode = getattr(user, "pricing_mode", None)
    if pricing_mode is None:
        # Fallback to the client_type if no specific pricing_mode is set
        pricing_mode = client_type
    return CurrentClient(client_type=client_type, pricing_mode=pricing_mode)