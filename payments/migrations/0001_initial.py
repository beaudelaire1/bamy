"""Initial migration for the Payment model.

This migration introduces the :class:`Payment` model, which stores
transaction data for various payment providers (PayPal, Stripe, etc.). Each
payment may be associated with a local order via a foreign key. The
model records the provider, external transaction ID, monetary amount,
currency, status and timestamps.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("orders", "0002_order_coupon_code_order_discount"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        help_text="Commande associée à ce paiement, si connue.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payments",
                        to="orders.order",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        choices=[("paypal", "PayPal"), ("stripe", "Stripe"), ("other", "Autre")],
                        default="other",
                        help_text="Prestataire de paiement utilisé.",
                        max_length=20,
                    ),
                ),
                (
                    "transaction_id",
                    models.CharField(
                        help_text="Identifiant retourné par l'API du prestataire.",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Montant du paiement.",
                        max_digits=10,
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        default="EUR",
                        help_text="Devise du paiement (ISO 4217).",
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default="pending",
                        help_text="Statut du paiement (pending, completed, failed).",
                        max_length=20,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]