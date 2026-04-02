from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.TextChoices):
    GB = 'GB', _('United Kingdom of Great Britain and Northern Ireland')
    US = 'US', _('United States')
    CA = 'CA', _('Canada')
    AU = 'AU', _('Australia')
    IN = 'IN', _('India')
    JP = 'JP', _('Japan')
    CN = 'CN', _('China')
    SG = 'SG', _('Singapore')
    AE = 'AE', _('United Arab Emirates')
    SA = 'SA', _('Saudi Arabia')
    DE = 'DE', _('Germany')
    FR = 'FR', _('France')
    IT = 'IT', _('Italy')
    ES = 'ES', _('Spain')
    NL = 'NL', _('Netherlands')
    SE = 'SE', _('Sweden')
    CH = 'CH', _('Switzerland')
    BR = 'BR', _('Brazil')
    MX = 'MX', _('Mexico')
    ZA = 'ZA', _('South Africa')
    NZ = 'NZ', _('New Zealand')


class AddressType(models.TextChoices):
    BILLING = 'BILLING', _('Billing')
    SHIPPING = 'SHIPPING', _('Shipping')
    RETURN = 'RETURN', _('Return')


class UserRole(models.TextChoices):
    CUSTOMER = 'CUSTOMER', _('Customer')
    ADMIN = 'ADMIN', _('Admin')
    VENDOR = 'VENDOR', _('Vendor')
    SUPPORT = 'SUPPORT', _('Support')


class ReviewModerationStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    APPROVED = 'APPROVED', _('Approved')
    REJECTED = 'REJECTED', _('Rejected')


class LoyaltyTransactionType(models.TextChoices):
    EARN = 'EARN', _('Earn')
    REDEEM = 'REDEEM', _('Redeem')
    EXPIRE = 'EXPIRE', _('Expire')
    ADJUST = 'ADJUST', _('Adjust')
