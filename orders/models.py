from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("paid", "Payée"),
        ("canceled", "Annulée"),
        ("refunded", "Remboursée"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")

    # Infos client
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True, default="")
    company = models.CharField(max_length=255, blank=True, default="")

    # Adresse (livraison = facturation pour cette V1)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=60, default="France")

    notes = models.TextField(blank=True, default="")

    # Totaux
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Coupon appliqué et montant de remise
    coupon_code = models.CharField(max_length=20, blank=True, default="")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Format lisible YYYYMMDD-HHMM-XXXX
            stamp = timezone.now().strftime("%Y%m%d-%H%M")
            seq = (Order.objects.filter(created_at__date=timezone.now().date()).count() + 1)
            self.order_number = f"{stamp}-{seq:04d}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_title = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=64)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_title} x{self.quantity}"
