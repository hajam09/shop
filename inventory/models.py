from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel


class InventoryMovement(BaseModel):
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='inventoryMovements')
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, blank=True, null=True,
                                related_name='inventoryMovements')
    orderItem = models.ForeignKey('orders.OrderItem', on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name='inventoryMovements')
    quantityDelta = models.IntegerField()
    reason = models.CharField(max_length=64)
    resultingStock = models.IntegerField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['product', 'createdAt']), models.Index(fields=['variant', 'createdAt']),
                   models.Index(fields=['orderItem'])]


class StockAlert(BaseModel):
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='stockAlerts')
    threshold = models.PositiveIntegerField(default=5)
    isActive = models.BooleanField(default=True)
    lastTriggeredAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['isActive', 'lastTriggeredAt'])]


class BackInStockSubscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backInStockSubscriptions')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='backInStockSubscribers')
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, blank=True, null=True,
                                related_name='backInStockSubscribers')
    isNotified = models.BooleanField(default=False)
    notifiedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'product', 'variant')
        indexes = [models.Index(fields=['product', 'isNotified']), models.Index(fields=['variant', 'isNotified'])]
