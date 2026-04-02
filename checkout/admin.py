from django.contrib import admin

from checkout.models import (
    Cart,
    CartItem,
    DeliveryOption,
)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    pass


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):
    pass
