import random

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from orders.choices import InvoiceStatus, ReturnStatus, Status
from payments.choices import Currency


def generateOrderNumber():
    return random.randint(1000000000, 9999999999)


class Order(BaseModel):
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, related_name='productOrders')
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='buyerOrders')
    paymentMethod = models.ForeignKey('payments.PaymentMethod', on_delete=models.SET_NULL, related_name='orders', blank=True, null=True)
    shippingAddress = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, related_name='shippingOrders', blank=True, null=True)
    billingAddress = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, related_name='billingOrders', blank=True, null=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ORDERED)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    unitPrice = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    taxAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shippingAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discountAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    number = models.CharField(max_length=16, unique=True, default=generateOrderNumber)
    quantity = models.PositiveIntegerField(default=1)
    tracking = models.CharField(blank=True, null=True, max_length=64)
    trackingCarrier = models.CharField(max_length=64, blank=True, null=True)
    placedAt = models.DateTimeField(default=timezone.now)
    paidAt = models.DateTimeField(blank=True, null=True)
    shippedAt = models.DateTimeField(blank=True, null=True)
    deliveredAt = models.DateTimeField(blank=True, null=True)
    customerNote = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['buyer', 'createdAt']), models.Index(fields=['status', 'createdAt']), models.Index(fields=['number'])]


class OrderStatus(BaseModel):
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ORDERED)
    description = models.TextField(blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderStatus')
    changedBy = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orderStatusChanges', blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['order', 'createdAt']), models.Index(fields=['status', 'createdAt'])]


class Note(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderNotes')
    summary = models.CharField(max_length=255)
    description = models.TextField()
    isInternal = models.BooleanField(default=True)
    createdBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orderNotes')


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, related_name='orderItems')
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, blank=True, null=True, related_name='orderItems')
    titleSnapshot = models.CharField(max_length=255)
    skuSnapshot = models.CharField(max_length=64, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unitPrice = models.DecimalField(max_digits=12, decimal_places=2)
    taxAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discountAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    lineTotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=['order', 'createdAt']), models.Index(fields=['product']), models.Index(fields=['variant'])]


class OrderShipment(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    deliveryOption = models.ForeignKey('checkout.DeliveryOption', on_delete=models.SET_NULL, blank=True, null=True, related_name='shipments')
    trackingNumber = models.CharField(max_length=64, blank=True, null=True)
    trackingUrl = models.URLField(max_length=512, blank=True, null=True)
    carrier = models.CharField(max_length=64, blank=True, null=True)
    shippedAt = models.DateTimeField(blank=True, null=True)
    deliveredAt = models.DateTimeField(blank=True, null=True)
    statusText = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['order', 'createdAt']), models.Index(fields=['trackingNumber']), models.Index(fields=['carrier', 'shippedAt'])]


class Invoice(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='invoices')
    invoiceNumber = models.CharField(max_length=32, unique=True)
    status = models.CharField(max_length=16, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    issueDate = models.DateField(default=timezone.now)
    dueDate = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    taxAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shippingAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discountAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    totalAmount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    pdfUrl = models.URLField(max_length=512, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['order', 'issueDate']), models.Index(fields=['status', 'issueDate'])]


class ReturnRequest(BaseModel):
    orderItem = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='returnRequests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='returnRequests')
    status = models.CharField(max_length=16, choices=ReturnStatus.choices, default=ReturnStatus.REQUESTED)
    reason = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    requestedRefundAmount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    approvedRefundAmount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    courierLabelUrl = models.URLField(max_length=512, blank=True, null=True)
    processedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'status']), models.Index(fields=['orderItem', 'status']), models.Index(fields=['status', 'createdAt'])]
