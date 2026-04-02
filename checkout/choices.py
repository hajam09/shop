from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryMethod(models.TextChoices):
    STANDARD = 'STANDARD', _('Standard')
    EXPRESS = 'EXPRESS', _('Express')
    SAME_DAY = 'SAME_DAY', _('Same Day')
    CLICK_AND_COLLECT = 'CLICK_AND_COLLECT', _('Click and Collect')
