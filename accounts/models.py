from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from accounts.choices import AddressType, Country, LoyaltyTransactionType, ReviewModerationStatus, UserRole
from catalog.models import Product, ProductVariant
from core.models import BaseModel


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    fullName = models.CharField(max_length=128)
    phoneNumber = models.CharField(max_length=32, blank=True, null=True, validators=[RegexValidator(regex=r'^[0-9+\-() ]+$')])
    addressLine1 = models.CharField(max_length=255)
    addressLine2 = models.CharField(max_length=255, blank=True, null=True)
    addressLine3 = models.CharField(max_length=255, blank=True, null=True)
    town = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128)
    county = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=2, choices=Country.choices, default=Country.GB)
    isPrimary = models.BooleanField(default=False)
    type = models.CharField(max_length=16, choices=AddressType.choices, default=AddressType.SHIPPING)
    deliveryInstructions = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['postcode', 'country'])
        ]
        verbose_name = 'Address'
        verbose_name_plural = 'Address'


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=16, choices=UserRole.choices, default=UserRole.CUSTOMER)
    phoneNumber = models.CharField(max_length=32, blank=True, null=True)
    isEmailVerified = models.BooleanField(default=False)
    isPhoneVerified = models.BooleanField(default=False)
    isBlocked = models.BooleanField(default=False)
    twoFactorEnabled = models.BooleanField(default=False)
    marketingConsent = models.BooleanField(default=False)
    gdprConsentAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['role', 'isBlocked'])]


class VendorProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendorProfile')
    storeName = models.CharField(max_length=255)
    legalName = models.CharField(max_length=255, blank=True, null=True)
    taxId = models.CharField(max_length=64, blank=True, null=True)
    supportEmail = models.EmailField(blank=True, null=True)
    supportPhone = models.CharField(max_length=32, blank=True, null=True)
    commissionRate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0), MaxValueValidator(100)])
    isApproved = models.BooleanField(default=False)
    approvedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['isApproved', 'approvedAt'])]


class ProductViewHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewHistory')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='viewedByUsers')
    viewedAt = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=['user', 'viewedAt']), models.Index(fields=['product', 'viewedAt'])]


class ProductSearchHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searchHistory')
    query = models.CharField(max_length=255)
    filters = models.JSONField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'createdAt']), models.Index(fields=['query'])]


class Wishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    name = models.CharField(max_length=100, default='Default')
    isDefault = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'isDefault'])
        ]
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlist'


class WishlistItem(BaseModel):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlistedItems')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, blank=True, null=True, related_name='wishlistedItems')

    class Meta:
        unique_together = ('wishlist', 'product', 'variant')
        indexes = [
            models.Index(fields=['product'])
        ]
        verbose_name = 'WishlistItem'
        verbose_name_plural = 'WishlistItem'


class Review(BaseModel):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='orderReviews')
    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    isVerifiedPurchase = models.BooleanField(default=True)
    isVisible = models.BooleanField(default=True)
    moderationStatus = models.CharField(max_length=16, choices=ReviewModerationStatus.choices, default=ReviewModerationStatus.PENDING)
    moderatedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderatedReviews')
    moderatedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['order', 'createdAt']), models.Index(fields=['moderationStatus', 'isVisible'])]


class LoyaltyWallet(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyaltyWallet')
    pointsBalance = models.IntegerField(default=0)
    lifetimePoints = models.IntegerField(default=0)


class LoyaltyTransaction(BaseModel):
    wallet = models.ForeignKey(LoyaltyWallet, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, blank=True, null=True, related_name='loyaltyTransactions')
    type = models.CharField(max_length=10, choices=LoyaltyTransactionType.choices)
    points = models.IntegerField()
    expiresAt = models.DateTimeField(blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['wallet', 'createdAt']), models.Index(fields=['type', 'expiresAt'])]
