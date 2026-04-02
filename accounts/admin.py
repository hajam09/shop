from django.contrib import admin

from accounts.models import (
    Address,
    UserProfile,
    VendorProfile,
    ProductViewHistory,
    ProductSearchHistory,
    Wishlist,
    WishlistItem,
    Review,
    LoyaltyWallet,
    LoyaltyTransaction,
)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductViewHistory)
class ProductViewHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductSearchHistory)
class ProductSearchHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    pass


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(LoyaltyWallet)
class LoyaltyWalletAdmin(admin.ModelAdmin):
    pass


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    pass
