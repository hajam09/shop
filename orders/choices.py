from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    ORDERED = 'ORDERED', _('Ordered')
    PROCESSING = 'PROCESSING', _('Processing')
    PAYMENT_PENDING = 'PAYMENT_PENDING', _('Payment Pending')
    PAYMENT_FAILED = 'PAYMENT_FAILED', _('Payment Failed')
    CANCELLED = 'CANCELLED', _('Cancelled')
    DISPATCHED = 'DISPATCHED', _('Dispatched')
    IN_TRANSIT = 'IN_TRANSIT', _('In Transit')
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', _('Out for Delivery')
    DELIVERED = 'DELIVERED', _('Delivered')
    DISPUTED = 'DISPUTED', _('Disputed')
    RETURN_STARTED = 'RETURN_STARTED', _('Return Started')
    RETURN_ACCEPTED = 'RETURN_ACCEPTED', _('Return Accepted')
    RETURN_REJECTED = 'RETURN_REJECTED', _('Return Rejected')
    RETURNED = 'RETURNED', _('Returned')
    REFUNDED = 'REFUNDED', _('Refunded')


class InvoiceStatus(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    ISSUED = 'ISSUED', _('Issued')
    PAID = 'PAID', _('Paid')
    VOID = 'VOID', _('Void')
    REFUNDED = 'REFUNDED', _('Refunded')


class ReturnStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', _('Requested')
    APPROVED = 'APPROVED', _('Approved')
    REJECTED = 'REJECTED', _('Rejected')
    RECEIVED = 'RECEIVED', _('Received')
    REFUNDED = 'REFUNDED', _('Refunded')
    EXCHANGED = 'EXCHANGED', _('Exchanged')
