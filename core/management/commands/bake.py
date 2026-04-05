import random
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from accounts.models import Address
from accounts.choices import Country, AddressType
from catalog.choices import Condition, StockStatus
from catalog.models import Category, Product, ProductCategory
from payments.choices import Currency


class Command(BaseCommand):
    help = "Seed Users, Addresses, Categories, and Products (fresh DB)"

    NUMBER_OF_USERS = 5
    ADDRESSES_PER_USER = 2
    NUMBER_OF_PRODUCTS = 15

    # (slug, name, parent_slug_or_none, sort_order)
    CATEGORY_SEED = (
        ('electronics', 'Electronics', None, 0),
        ('electronics-computers', 'Computers', 'electronics', 0),
        ('electronics-computers-laptops', 'Laptops', 'electronics-computers', 0),
        ('electronics-computers-desktops', 'Desktops', 'electronics-computers', 1),
        ('electronics-computers-aio', 'AIO', 'electronics-computers', 2),
        ('electronics-phones', 'Phones', 'electronics', 1),
        ('electronics-phones-smartphones', 'Smartphones', 'electronics-phones', 0),
        ('home', 'Home', None, 1),
        ('home-kitchen', 'Kitchen', 'home', 0),
        ('home-kitchen-appliances', 'Appliances', 'home-kitchen', 0),
    )

    def handle(self, *args, **kwargs):
        faker = Faker()

        with transaction.atomic():
            users = self.create_users(faker)
            self.create_addresses(users, faker)
            categories = self.create_categories()
            self.create_products(users, categories, faker)

        self.stdout.write(
            self.style.SUCCESS(
                'Seeded: users, addresses, categories (tree), and products with category links.'
            )
        )

    def create_users(self, faker):
        user_bulk = []

        for i in range(Command.NUMBER_OF_USERS):
            user = User(
                username=faker.unique.user_name(),
                email=faker.unique.email(),
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                is_active=True,
            )

            user.set_password('password123')

            user_bulk.append(user)

        User.objects.bulk_create(user_bulk, batch_size=500)

        return list(User.objects.all())

    def create_addresses(self, users, faker):
        address_bulk = []

        for user in users:
            primary_index = random.randint(0, Command.ADDRESSES_PER_USER - 1)

            for i in range(Command.ADDRESSES_PER_USER):
                address = Address(
                    user=user,
                    fullName=faker.name(),
                    phoneNumber=self.generate_phone(faker),
                    addressLine1=faker.street_address(),
                    addressLine2=faker.secondary_address() if random.choice([True, False]) else None,
                    addressLine3=None,
                    town=faker.city() if random.choice([True, False]) else None,
                    city=faker.city(),
                    county=faker.state() if random.choice([True, False]) else None,
                    state=faker.state() if random.choice([True, False]) else None,
                    postcode=faker.postcode(),
                    country=random.choice(Country.values),
                    isPrimary=(i == primary_index),
                    type=random.choice(AddressType.values),
                    deliveryInstructions=faker.sentence(nb_words=6) if random.choice([True, False]) else None,
                )

                address_bulk.append(address)

        Address.objects.bulk_create(address_bulk, batch_size=500)

    def create_categories(self):
        by_slug = {}
        for slug, name, parent_slug, sort_order in self.CATEGORY_SEED:
            parent = by_slug[parent_slug] if parent_slug else None
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'parent': parent,
                    'sortOrder': sort_order,
                    'isActive': True,
                    'description': '',
                },
            )
            by_slug[slug] = cat
        return list(by_slug.values())

    def create_products(self, users, categories, faker):
        if not users or not categories:
            return

        for _ in range(Command.NUMBER_OF_PRODUCTS):
            seller = random.choice(users)
            title = faker.catch_phrase()
            if len(title) > 255:
                title = title[:252] + '...'

            base_slug = slugify(title)[:200] or f'product-{uuid.uuid4().hex[:8]}'
            slug = self._unique_product_slug(base_slug)

            product = Product.objects.create(
                seller=seller,
                title=title,
                slug=slug,
                sku=self._unique_sku(),
                brand=(faker.company()[:128]) if random.choice([True, True, False]) else '',
                category=random.choice(categories).name[:128],
                description=faker.text(max_nb_chars=500),
                currency=Currency.GBP,
                price=Decimal(str(round(random.uniform(4.99, 1299.99), 2))),
                compareAtPrice=Decimal(str(round(random.uniform(10, 1500), 2)))
                if random.choice([True, False])
                else None,
                condition=random.choice([c[0] for c in Condition.choices]),
                stock=random.randint(0, 200),
                minOrderQuantity=1,
                stockStatus=StockStatus.IN_STOCK,
                isActive=True,
                isFeatured=random.choice([True, False, False, False]),
            )

            pc_cat = random.choice(categories)
            ProductCategory.objects.create(
                product=product,
                category=pc_cat,
                isPrimary=True,
            )

    def _unique_product_slug(self, base: str) -> str:
        slug = base
        n = 2
        while Product.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug[:320]

    def _unique_sku(self) -> str:
        for _ in range(1000):
            candidate = f'SKU-{uuid.uuid4().hex[:12].upper()}'
            if not Product.objects.filter(sku=candidate).exists():
                return candidate
        return f'SKU-{uuid.uuid4().hex}'

    def generate_phone(self, faker):
        return faker.numerify(text='+44##########')
