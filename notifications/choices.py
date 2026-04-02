from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationChannel(models.TextChoices):
    EMAIL = 'EMAIL', _('Email')
    SMS = 'SMS', _('SMS')
    PUSH = 'PUSH', _('Push')
    IN_APP = 'IN_APP', _('In App')
    WHATSAPP = 'WHATSAPP', _('WhatsApp')


class NotificationType(models.TextChoices):
    ORDER_CONFIRMATION = 'ORDER_CONFIRMATION', _('Order Confirmation')
    SHIPPING_UPDATE = 'SHIPPING_UPDATE', _('Shipping Update')
    PROMOTION = 'PROMOTION', _('Promotion')
    LOYALTY_UPDATE = 'LOYALTY_UPDATE', _('Loyalty Update')
    BACK_IN_STOCK = 'BACK_IN_STOCK', _('Back In Stock')
