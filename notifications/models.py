from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from notifications.choices import NotificationChannel, NotificationType


class NotificationTemplate(BaseModel):
    type = models.CharField(max_length=32, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    isActive = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['type', 'channel', 'isActive'])]
        unique_together = ('type', 'channel')


class UserNotificationPreference(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificationPreferences')
    type = models.CharField(max_length=32, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    isEnabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'type', 'channel')


class NotificationLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=32, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    providerMessageId = models.CharField(max_length=128, blank=True, null=True)
    isSent = models.BooleanField(default=False)
    sentAt = models.DateTimeField(blank=True, null=True)
    errorMessage = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'createdAt']),
            models.Index(fields=['type', 'channel', 'isSent']),
            models.Index(fields=['providerMessageId']),
        ]
