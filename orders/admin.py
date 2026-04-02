from django.contrib import admin

from orders.models import (
    Order,
    OrderStatus,
    Note,
    OrderItem,
    OrderShipment,
    Invoice,
    ReturnRequest,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderShipment)
class OrderShipmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    pass
