from django.contrib import admin

from notifications.models import (
    NotificationTemplate,
    UserNotificationPreference,
    NotificationLog,
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    pass


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    pass


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    pass