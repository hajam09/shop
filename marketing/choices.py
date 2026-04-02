from django.db import models
from django.utils.translation import gettext_lazy as _


class CouponType(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', _('Percentage')
    FIXED = 'FIXED', _('Fixed')
    FREE_SHIPPING = 'FREE_SHIPPING', _('Free Shipping')


class CouponScope(models.TextChoices):
    ORDER = 'ORDER', _('Order')
    PRODUCT = 'PRODUCT', _('Product')
    CATEGORY = 'CATEGORY', _('Category')
