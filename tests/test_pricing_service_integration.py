from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from userauths.models import User
from catalog.models import Product, PromoCatalog, PromoItem
from core.services.pricing_service import PromoAwareB2BPricingService
from core.adapters.orm_promo_adapter import DjangoPromoCatalogAdapter


class PromoAwarePricingServiceIntegrationTest(TestCase):
    """
    Tests d'intégration pour le service de pricing avec catalogues de promotions.

    Ces tests valident le comportement de ``PromoAwareB2BPricingService`` lorsqu'il
    interagit avec les modèles Django (Product, PromoCatalog, PromoItem) via
    l'adaptateur ORM. L'objectif est de garantir que les promos sont appliquées
    correctement selon les numéros clients, les types de clients et les périodes.
    """

    def setUp(self) -> None:
        # Service et produit de base utilisés dans plusieurs tests
        self.service = PromoAwareB2BPricingService(DjangoPromoCatalogAdapter())
        self.now = timezone.now()

        # Création des entités de référence pour satisfaire les FKs
        from catalog.models import Category, Brand
        self.category = Category.objects.create(name="Catégorie 1", slug="cat-1")
        self.brand = Brand.objects.create(name="Marque 1", slug="marque-1")

        # Crée un produit avec différentes grilles B2B
        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            sku="TP-001",
            article_code="AC-001",
            category=self.category,
            brand=self.brand,
            price=Decimal("100.00"),
            discount_price=None,
            price_wholesaler=Decimal("80.00"),
            price_big_retail=Decimal("90.00"),
            price_small_retail=Decimal("95.00"),
            stock=100,
        )

        # Crée un utilisateur B2B vérifié avec un numéro client
        self.user = User.objects.create_user(
            username="client1",
            email="client1@example.com",
            password="pass",
            customer_number="CUST1",
            client_type="wholesaler",
            is_b2b_verified=True,
        )

    def _create_active_catalog(self, **kwargs) -> PromoCatalog:
        """Helper pour créer un catalogue actif dans la période courante."""
        default = dict(
            title="PromoCat",
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
            is_active=True,
        )
        default.update(kwargs)
        return PromoCatalog.objects.create(**default)

    def test_catalog_promo_applied_for_allowed_customer_number(self) -> None:
        """La promo catalogue s'applique lorsque le numéro client est ciblé."""
        cat = self._create_active_catalog()
        # Promo ciblée explicitement par numéro client
        PromoItem.objects.create(
            catalog=cat,
            product=self.product,
            promo_price=Decimal("70.00"),
            allowed_customer_numbers=["CUST1"],
        )
        price = self.service.get_unit_price(self.product, self.user)
        self.assertEqual(price, Decimal("70.00"))

    def test_no_applicable_promo_falls_back_to_b2b(self) -> None:
        """Si aucune promo applicable, le prix B2B est utilisé."""
        # Promo avec un autre numéro client ne doit pas s'appliquer
        cat = self._create_active_catalog()
        PromoItem.objects.create(
            catalog=cat,
            product=self.product,
            promo_price=Decimal("70.00"),
            allowed_customer_numbers=["OTHER"],
        )
        price = self.service.get_unit_price(self.product, self.user)
        # L'utilisateur est un grossiste vérifié, on attend le tarif wholesaler
        self.assertEqual(price, Decimal("80.00"))

    def test_catalog_promo_targeted_by_client_type(self) -> None:
        """Une promo catalogue ciblée par type de client s'applique même sans numéro client."""
        # Utilisateur sans numéro client explicite
        user2 = User.objects.create_user(
            username="client2",
            email="client2@example.com",
            password="pass",
            customer_number=None,
            client_type="big_retail",
            is_b2b_verified=True,
        )
        # Promo ciblée par type de client (big_retail) ; allowed_customer_numbers vide
        cat = self._create_active_catalog(target_client_type="big_retail")
        PromoItem.objects.create(
            catalog=cat,
            product=self.product,
            promo_price=Decimal("85.00"),
            allowed_customer_numbers=[],
        )
        price = self.service.get_unit_price(self.product, user2)
        self.assertEqual(price, Decimal("85.00"))

    def test_choose_lowest_promo_when_multiple_applicable(self) -> None:
        """Lorsqu'il existe plusieurs promos applicables, la moins chère est retenue."""
        cat1 = self._create_active_catalog()
        cat2 = self._create_active_catalog()
        # Deux promos applicables pour le même client
        PromoItem.objects.create(
            catalog=cat1,
            product=self.product,
            promo_price=Decimal("72.00"),
            allowed_customer_numbers=["CUST1"],
        )
        PromoItem.objects.create(
            catalog=cat2,
            product=self.product,
            promo_price=Decimal("68.00"),
            allowed_customer_numbers=["CUST1"],
        )
        price = self.service.get_unit_price(self.product, self.user)
        # La promo la moins chère doit être sélectionnée
        self.assertEqual(price, Decimal("68.00"))