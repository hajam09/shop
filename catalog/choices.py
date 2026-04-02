from django.db import models
from django.utils.translation import gettext_lazy as _


class Condition(models.TextChoices):
    NEW = 'NEW', _('New')
    USED = 'USED', _('Used')
    OPENED_NEVER_USED = 'OPENED_NEVER_USED', _('Opened - never used')
    SELLER_REFURBISHED = 'SELLER_REFURBISHED', _('Seller refurbished')
    FOR_PARTS_OR_NOT_WORKING = 'FOR_PARTS_OR_NOT_WORKING', _('For parts or not working')


class StockStatus(models.TextChoices):
    IN_STOCK = 'IN_STOCK', _('In stock')
    LOW_STOCK = 'LOW_STOCK', _('Low stock')
    OUT_OF_STOCK = 'OUT_OF_STOCK', _('Out of stock')
    PREORDER = 'PREORDER', _('Preorder')
