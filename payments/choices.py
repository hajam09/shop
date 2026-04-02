from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.TextChoices):
    GBP = 'GBP', _('British Pound')
    USD = 'USD', _('US Dollar')
    EUR = 'EUR', _('Euro')
    CAD = 'CAD', _('Canadian Dollar')
    AUD = 'AUD', _('Australian Dollar')
    INR = 'INR', _('Indian Rupee')
    JPY = 'JPY', _('Japanese Yen')
    CNY = 'CNY', _('Chinese Yuan')
    SGD = 'SGD', _('Singapore Dollar')
    AED = 'AED', _('UAE Dirham')
    SAR = 'SAR', _('Saudi Riyal')
    CHF = 'CHF', _('Swiss Franc')
    SEK = 'SEK', _('Swedish Krona')
    NOK = 'NOK', _('Norwegian Krone')
    DKK = 'DKK', _('Danish Krone')
    NZD = 'NZD', _('New Zealand Dollar')
    BRL = 'BRL', _('Brazilian Real')
    MXN = 'MXN', _('Mexican Peso')
    ZAR = 'ZAR', _('South African Rand')
    HKD = 'HKD', _('Hong Kong Dollar')


class PaymentProvider(models.TextChoices):
    STRIPE = 'STRIPE', _('Stripe')
    PAYPAL = 'PAYPAL', _('PayPal')
    APPLE_PAY = 'APPLE_PAY', _('Apple Pay')
    GOOGLE_PAY = 'GOOGLE_PAY', _('Google Pay')
    RAZORPAY = 'RAZORPAY', _('Razorpay')
    PAYTM = 'PAYTM', _('Paytm')
    PHONEPE = 'PHONEPE', _('PhonePe')
    UPI = 'UPI', _('UPI')
    KLARNA = 'KLARNA', _('Klarna')
    AFTERPAY = 'AFTERPAY', _('Afterpay')
    AMAZON_PAY = 'AMAZON_PAY', _('Amazon Pay')
    BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY', _('Cash on Delivery')


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    AUTHORIZED = 'AUTHORIZED', _('Authorized')
    CAPTURED = 'CAPTURED', _('Captured')
    FAILED = 'FAILED', _('Failed')
    REFUNDED = 'REFUNDED', _('Refunded')
    PARTIALLY_REFUNDED = 'PARTIALLY_REFUNDED', _('Partially Refunded')


class PayoutStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    PAID = 'PAID', _('Paid')
    FAILED = 'FAILED', _('Failed')
