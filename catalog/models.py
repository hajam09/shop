from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from catalog.choices import Condition, StockStatus
from payments.choices import Currency


class Product(BaseModel):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sellerProducts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=320, unique=True)
    sku = models.CharField(max_length=64, unique=True)
    brand = models.CharField(max_length=128, blank=True, null=True)
    category = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    expireDate = models.DateTimeField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.GBP)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compareAtPrice = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    costPrice = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    deliveryCharge = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    taxRate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0), MaxValueValidator(100)])
    condition = models.CharField(max_length=32, choices=Condition.choices, default=Condition.NEW)
    stock = models.PositiveIntegerField(default=0)
    minOrderQuantity = models.PositiveIntegerField(default=1)
    maxOrderQuantity = models.PositiveIntegerField(blank=True, null=True)
    stockStatus = models.CharField(max_length=20, choices=StockStatus.choices, default=StockStatus.IN_STOCK)
    weightGrams = models.PositiveIntegerField(blank=True, null=True)
    isDigital = models.BooleanField(default=False)
    isActive = models.BooleanField(default=True)
    isFeatured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def isExpired(self):
        return bool(self.expireDate and self.expireDate <= timezone.now())

    class Meta:
        indexes = [
            models.Index(fields=['seller', 'isActive']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'brand']),
            models.Index(fields=['stockStatus']),
        ]


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productImages')
    image = models.ImageField(upload_to='uploads/%Y/%m/%d')
    altText = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    isPrimary = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['product', 'order']), models.Index(fields=['product', 'isPrimary'])]


class Category(BaseModel):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=160, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subcategories', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    isActive = models.BooleanField(default=True)
    sortOrder = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_full_path(self):
        parts = []
        node = self
        for _ in range(128):
            if node is None:
                break
            parts.append(node.name)
            node = node.parent if node.parent_id else None
        return ' -> '.join(reversed(parts))

    class Meta:
        indexes = [models.Index(fields=['parent', 'sortOrder']), models.Index(fields=['slug'])]


class ProductCategory(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productCategories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categoryProducts')
    isPrimary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'category')
        indexes = [models.Index(fields=['category', 'isPrimary'])]


class ProductTag(BaseModel):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True)


class ProductTagMap(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productTags')
    tag = models.ForeignKey(ProductTag, on_delete=models.CASCADE, related_name='tagProducts')

    class Meta:
        unique_together = ('product', 'tag')
        indexes = [models.Index(fields=['tag', 'product'])]


class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=128)
    sku = models.CharField(max_length=64, unique=True)
    color = models.CharField(max_length=64, blank=True, null=True)
    size = models.CharField(max_length=64, blank=True, null=True)
    modelNumber = models.CharField(max_length=64, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    weightGrams = models.PositiveIntegerField(blank=True, null=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['product', 'isActive']), models.Index(fields=['product', 'stock'])]


class ProductVideo(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(max_length=512)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=['product', 'order'])]


class ProductComparison(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    name = models.CharField(max_length=100, default='Default')

    class Meta:
        indexes = [models.Index(fields=['user', 'name'])]


class ProductComparisonItem(BaseModel):
    comparison = models.ForeignKey(ProductComparison, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comparisonItems')

    class Meta:
        unique_together = ('comparison', 'product')


class ProductQuestion(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productQuestions')
    question = models.TextField()
    isVisible = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['product', 'isVisible', 'createdAt']), models.Index(fields=['user', 'createdAt'])]


class ProductAnswer(BaseModel):
    question = models.OneToOneField(ProductQuestion, on_delete=models.CASCADE, related_name='answer')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productAnswers')
    answer = models.TextField()
    isSellerResponse = models.BooleanField(default=False)
    isVisible = models.BooleanField(default=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'createdAt'])]


class RecommendedProduct(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommendedToUsers')
    score = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000)
    reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'product')
        indexes = [models.Index(fields=['user', '-score']), models.Index(fields=['product', '-score'])]
