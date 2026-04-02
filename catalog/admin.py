from django.contrib import admin

from catalog.models import (
    Product,
    ProductImage,
    Category,
    ProductCategory,
    ProductTag,
    ProductTagMap,
    ProductVariant,
    ProductVideo,
    ProductComparison,
    ProductComparisonItem,
    ProductQuestion,
    ProductAnswer,
    RecommendedProduct,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductTagMap)
class ProductTagMapAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductComparison)
class ProductComparisonAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductComparisonItem)
class ProductComparisonItemAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductAnswer)
class ProductAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(RecommendedProduct)
class RecommendedProductAdmin(admin.ModelAdmin):
    pass
