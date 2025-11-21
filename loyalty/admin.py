from django.contrib import admin
from .models import LoyaltyAccount, Coupon


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "updated_at")
    search_fields = ("user__username",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "expires_at", "is_active")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)