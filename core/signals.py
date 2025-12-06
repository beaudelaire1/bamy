"""
Custom application signals for decoupled cross‑app communication.

The ``order_validated`` signal is emitted whenever an order has been
successfully created and validated.  Applications such as loyalty or
notifications can subscribe to this signal to perform side effects
(e.g. awarding loyalty points) without coupling the orders app to
those implementations.
"""

from django.dispatch import Signal

# Sent after an order has been created and validated.  Receivers should
# accept ``order`` and ``user`` keyword arguments.
order_validated = Signal()