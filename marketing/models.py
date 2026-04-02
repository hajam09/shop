from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from marketing.choices import CouponScope, CouponType


class Coupon(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=20, choices=CouponType.choices, default=CouponType.PERCENTAGE)
    scope = models.CharField(max_length=16, choices=CouponScope.choices, default=CouponScope.ORDER)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    maxDiscountAmount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    minOrderAmount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    startAt = models.DateTimeField(blank=True, null=True)
    endAt = models.DateTimeField(blank=True, null=True)
    usageLimit = models.PositiveIntegerField(blank=True, null=True)
    usagePerUser = models.PositiveIntegerField(blank=True, null=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['isActive', 'startAt', 'endAt']), models.Index(fields=['scope', 'type'])]


class CouponUsage(BaseModel):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='couponUsages')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='couponUsages')
    discountAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        indexes = [models.Index(fields=['coupon', 'user']), models.Index(fields=['order'])]
        unique_together = ('coupon', 'user', 'order')


class ReferralProgram(BaseModel):
    name = models.CharField(max_length=128)
    codePrefix = models.CharField(max_length=20, blank=True, null=True)
    rewardPoints = models.PositiveIntegerField(default=0)
    rewardAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    isActive = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['isActive'])]


class Referral(BaseModel):
    program = models.ForeignKey(ReferralProgram, on_delete=models.CASCADE, related_name='referrals')
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sentReferrals')
    referredUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receivedReferrals')
    code = models.CharField(max_length=64, unique=True)
    isConverted = models.BooleanField(default=False)
    convertedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['referrer', 'isConverted']), models.Index(fields=['referredUser'])]
        unique_together = ('program', 'referrer', 'referredUser')
