from django.contrib import admin

from inventory.models import (
    InventoryMovement,
    StockAlert,
    BackInStockSubscription,
)


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    pass


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    pass


@admin.register(BackInStockSubscription)
class BackInStockSubscriptionAdmin(admin.ModelAdmin):
    pass