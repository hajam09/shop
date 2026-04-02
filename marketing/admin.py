from django.contrib import admin

from marketing.models import (
    Coupon,
    CouponUsage,
    ReferralProgram,
    Referral,
)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    pass


@admin.register(ReferralProgram)
class ReferralProgramAdmin(admin.ModelAdmin):
    pass


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    pass