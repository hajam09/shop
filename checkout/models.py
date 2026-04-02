from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from checkout.choices import DeliveryMethod
from payments.choices import Currency


class DeliveryOption(BaseModel):
    name = models.CharField(max_length=64)
    method = models.CharField(max_length=24, choices=DeliveryMethod.choices, default=DeliveryMethod.STANDARD)
    provider = models.CharField(max_length=64, blank=True, null=True)
    minDeliveryDays = models.PositiveSmallIntegerField(default=2)
    maxDeliveryDays = models.PositiveSmallIntegerField(default=5)
    basePrice = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    isActive = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['method', 'isActive'])]


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', blank=True, null=True)
    sessionKey = models.CharField(max_length=128, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    coupon = models.ForeignKey('marketing.Coupon', on_delete=models.SET_NULL, blank=True, null=True, related_name='appliedCarts')
    isCheckedOut = models.BooleanField(default=False)
    checkedOutAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'isCheckedOut']), models.Index(fields=['sessionKey', 'isCheckedOut'])]


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, related_name='cartItems')
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, blank=True, null=True, related_name='cartItems')
    quantity = models.PositiveIntegerField(default=1)
    unitPrice = models.DecimalField(max_digits=12, decimal_places=2)
    lineTotal = models.DecimalField(max_digits=12, decimal_places=2)
    saveForLater = models.BooleanField(default=False)

    class Meta:
        unique_together = ('cart', 'product', 'variant')
        indexes = [models.Index(fields=['cart', 'saveForLater']), models.Index(fields=['product'])]
