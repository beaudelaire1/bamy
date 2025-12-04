"""
Clients app for Xeros B2B
This module defines the multi‑company entities that power the B2B
platform.  It introduces the notion of a ``Client`` (i.e. a
customer organisation) and a ``UserClientLink`` mapping Django users
to those clients with role‑based permissions.

The goal of this package is to encapsulate all domain logic related
to governing access to catalogues, promotions and ordering on a
per‑client basis.
"""
