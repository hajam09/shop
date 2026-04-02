from django.contrib import admin

from payments.models import (
    PaymentMethod,
    PaymentTransaction,
    GiftCard,
    GiftCardTransaction,
    VendorPayout,
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    pass


@admin.register(GiftCardTransaction)
class GiftCardTransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(VendorPayout)
class VendorPayoutAdmin(admin.ModelAdmin):
    pass
