from cryptography.fernet import Fernet
from decouple import config
from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from payments.choices import Currency, PaymentProvider, PaymentStatus, PayoutStatus


class PaymentMethod(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paymentMethods')
    number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=3)
    name = models.CharField(max_length=128)
    billingZip = models.CharField(max_length=20, blank=True, null=True)
    expiration = models.DateField()
    isPrimary = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)

    def setCardNumber(self, number):
        fernet = Fernet(bytes(config('FERNET_KEY', cast=str), 'utf-8'))
        self.number = fernet.encrypt(bytes(number, 'utf-8')).decode('utf-8')

    @property
    def getCardNumber(self):
        fernet = Fernet(bytes(config('FERNET_KEY', cast=str), 'utf-8'))
        return fernet.decrypt(bytes(self.number, 'utf-8')).decode('utf-8')

    def setCvvNumber(self, number):
        fernet = Fernet(bytes(config('FERNET_KEY', cast=str), 'utf-8'))
        self.cvv = fernet.encrypt(bytes(number, 'utf-8')).decode('utf-8')

    @property
    def getCvvNumber(self):
        fernet = Fernet(bytes(config('FERNET_KEY', cast=str), 'utf-8'))
        return fernet.decrypt(bytes(self.cvv, 'utf-8')).decode('utf-8')

    @property
    def maskedCardNumber(self) -> str:
        """
        Display-only masked representation like: **** **** **** 1234
        """
        try:
            digits = ''.join(ch for ch in (self.getCardNumber or '') if ch.isdigit())
        except Exception:
            digits = ''
        last4 = digits[-4:] if len(digits) >= 4 else digits
        if not last4:
            return '—'
        return f'**** **** **** {last4}'

    class Meta:
        indexes = [
            models.Index(fields=['user', 'isPrimary']),
            models.Index(fields=['user', 'isActive']),
        ]


class PaymentTransaction(BaseModel):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='paymentTransactions')
    provider = models.CharField(max_length=32, choices=PaymentProvider.choices, default=PaymentProvider.STRIPE)
    status = models.CharField(max_length=32, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    providerReference = models.CharField(max_length=128, blank=True, null=True)
    responsePayload = models.JSONField(blank=True, null=True)
    failureReason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'createdAt']),
            models.Index(fields=['status', 'createdAt']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['providerReference']),
        ]


class GiftCard(BaseModel):
    code = models.CharField(max_length=64, unique=True)
    initialBalance = models.DecimalField(max_digits=12, decimal_places=2)
    currentBalance = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    isActive = models.BooleanField(default=True)
    expiresAt = models.DateTimeField(blank=True, null=True)
    purchasedBy = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='purchasedGiftCards')
    assignedTo = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='giftCards')

    class Meta:
        indexes = [models.Index(fields=['assignedTo', 'isActive']), models.Index(fields=['isActive', 'expiresAt'])]


class GiftCardTransaction(BaseModel):
    giftCard = models.ForeignKey(GiftCard, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, blank=True, null=True, related_name='giftCardTransactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balanceAfter = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['giftCard', 'createdAt']), models.Index(fields=['order'])]


class VendorPayout(BaseModel):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendorPayouts')
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    totalAmount = models.DecimalField(max_digits=12, decimal_places=2)
    feeAmount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    netAmount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=16, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    paidAt = models.DateTimeField(blank=True, null=True)
    reference = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['vendor', 'status', 'createdAt']),
            models.Index(fields=['status', 'paidAt']),
            models.Index(fields=['reference']),
        ]
