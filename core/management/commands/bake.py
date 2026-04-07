import random
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from accounts.models import Address, Wishlist, WishlistItem
from accounts.choices import Country, AddressType
from catalog.choices import Condition, StockStatus
from catalog.models import Category, Product, ProductCategory, ProductImage, ProductVariant
from payments.choices import Currency
from checkout.models import DeliveryOption
from checkout.choices import DeliveryMethod


class Command(BaseCommand):
    help = "Seed Users, Addresses, Categories, and Products (fresh DB)"

    NUMBER_OF_USERS = 5
    ADDRESSES_PER_USER = 2
    NUMBER_OF_PRODUCTS = 200

    # (slug, name, parent_slug_or_none, sort_order)
    CATEGORY_SEED = (
        ('electronics', 'Electronics', None, 0),
        ('electronics-computers', 'Computers', 'electronics', 0),
        ('electronics-computers-laptops', 'Laptops', 'electronics-computers', 0),
        ('electronics-computers-desktops', 'Desktops', 'electronics-computers', 1),
        ('electronics-computers-aio', 'AIO', 'electronics-computers', 2),
        ('electronics-phones', 'Phones', 'electronics', 1),
        ('electronics-phones-smartphones', 'Smartphones', 'electronics-phones', 0),
        ('electronics-components', 'Components', 'electronics', 2),
        ('electronics-components-cpu', 'CPU', 'electronics-components', 0),
        ('electronics-components-gpu', 'GPU', 'electronics-components', 1),
        ('electronics-components-motherboard', 'Motherboards', 'electronics-components', 2),
        ('electronics-components-ram', 'Memory', 'electronics-components', 3),
        ('electronics-components-storage', 'Storage', 'electronics-components', 4),
        ('electronics-components-psu', 'Power Supplies', 'electronics-components', 5),
        ('electronics-components-cooling', 'Cooling', 'electronics-components', 6),
        ('electronics-components-case', 'Cases', 'electronics-components', 7),
        ('home', 'Home', None, 1),
        ('home-kitchen', 'Kitchen', 'home', 0),
        ('home-kitchen-appliances', 'Appliances', 'home-kitchen', 0),
        ('home-garden', 'Garden', 'home', 1),
        ('home-garden-tools', 'Garden Tools', 'home-garden', 0),
        ('home-garden-outdoor', 'Outdoor Living', 'home-garden', 1),
        ('software', 'Software', None, 2),
        ('software-licenses', 'Licenses', 'software', 0),
    )

    BRAND_SEED = {
        'Smartphones': ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Sony', 'Motorola', 'Nokia'],
        'Laptops': ['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'Microsoft'],
        'Desktops': ['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI'],
        'AIO': ['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS'],
        'Appliances': ['Bosch', 'Samsung', 'LG', 'Whirlpool', 'Beko', 'Philips', 'Tefal', 'Breville'],
        'Kitchen': ['OXO', 'KitchenAid', 'Joseph Joseph', 'Tefal', 'Pyrex', 'Le Creuset'],
        'Electronics': ['Sony', 'Anker', 'JBL', 'Bose', 'Logitech', 'TP-Link', 'Razer'],
        'Home': ['IKEA', 'Dunelm', 'Habitat', 'Philips', 'Dyson'],
        'Computers': ['Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'Apple', 'Microsoft'],
        'Phones': ['Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi', 'Sony', 'Motorola'],
        'Components': ['Corsair', 'MSI', 'ASUS', 'Gigabyte', 'NZXT', 'Cooler Master', 'be quiet!', 'Seasonic'],
        'CPU': ['Intel', 'AMD'],
        'GPU': ['NVIDIA', 'AMD'],
        'Motherboards': ['ASUS', 'MSI', 'Gigabyte', 'ASRock'],
        'Memory': ['Corsair', 'Kingston', 'G.Skill', 'Crucial', 'TeamGroup'],
        'Storage': ['Samsung', 'Western Digital', 'Seagate', 'Crucial', 'Kingston'],
        'Power Supplies': ['Corsair', 'Seasonic', 'EVGA', 'be quiet!', 'Cooler Master'],
        'Cooling': ['Noctua', 'Cooler Master', 'NZXT', 'Corsair', 'Arctic'],
        'Cases': ['NZXT', 'Corsair', 'Fractal Design', 'Lian Li', 'Cooler Master'],
        'Garden': ['Gardena', 'Bosch', 'Fiskars', 'Kärcher', 'Black+Decker'],
        'Garden Tools': ['Bosch', 'Fiskars', 'Einhell', 'Ryobi', 'Black+Decker'],
        'Outdoor Living': ['Weber', 'Outsunny', 'Keter', 'Coleman', 'Dometic'],
        'Software': ['Microsoft', 'Adobe', 'JetBrains', 'Corel', 'McAfee', 'Bitdefender'],
        'Licenses': ['Microsoft', 'Adobe', 'JetBrains', 'Autodesk', 'Bitdefender', 'Kaspersky'],
    }

    PRODUCT_TEMPLATES = {
        'Smartphones': [
            ('{brand} {series} {storage} Smartphone', (199.99, 1299.99), (140, 230)),
            ('{brand} {series} {storage} 5G Phone', (229.99, 1399.99), (140, 230)),
        ],
        'Laptops': [
            ('{brand} {series} {screen}" Laptop ({cpu}/{ram}/{storage})', (349.99, 2499.99), (1100, 2600)),
            ('{brand} {series} Ultrabook {screen}" ({cpu}/{ram}/{storage})', (499.99, 2799.99), (900, 1800)),
        ],
        'Desktops': [
            ('{brand} {series} Desktop PC ({cpu}/{ram}/{storage})', (299.99, 2199.99), (3000, 12000)),
        ],
        'AIO': [
            ('{brand} {series} All‑in‑One {screen}" ({cpu}/{ram}/{storage})', (549.99, 2499.99), (3000, 9000)),
        ],
        'Appliances': [
            ('{brand} {series} Air Fryer {capacity}L', (39.99, 249.99), (2500, 8000)),
            ('{brand} {series} Kettle {capacity}L', (14.99, 79.99), (800, 1800)),
            ('{brand} {series} Toaster 2‑Slice', (14.99, 99.99), (900, 2200)),
        ],
        'Kitchen': [
            ('{brand} Non‑Stick Frying Pan {size}cm', (12.99, 79.99), (400, 1600)),
            ('{brand} Glass Storage Containers (Set of {count})', (9.99, 59.99), (600, 2200)),
        ],
        'Electronics': [
            ('{brand} Wireless Earbuds', (19.99, 299.99), (40, 90)),
            ('{brand} Bluetooth Speaker', (19.99, 399.99), (200, 2500)),
            ('{brand} USB‑C Charger {watt}W', (9.99, 89.99), (60, 300)),
        ],
        'Home': [
            ('{brand} LED Floor Lamp', (19.99, 149.99), (1200, 5200)),
            ('{brand} Throw Blanket {size}', (9.99, 79.99), (400, 1400)),
        ],
        'Computers': [
            ('{brand} {series} Monitor {screen}"', (79.99, 599.99), (2500, 9000)),
            ('{brand} Wireless Keyboard & Mouse', (14.99, 129.99), (200, 900)),
        ],
        'Phones': [
            ('{brand} Fast Charger {watt}W', (9.99, 79.99), (60, 350)),
            ('{brand} Protective Case for {series}', (6.99, 39.99), (20, 120)),
        ],
        'CPU': [
            ('{brand} {cpu_series} {cpu_model} Processor', (89.99, 699.99), (150, 600)),
        ],
        'GPU': [
            ('{brand} {gpu_series} Graphics Card {vram}GB', (169.99, 1999.99), (800, 2600)),
        ],
        'Motherboards': [
            ('{brand} {chipset} Motherboard ({socket})', (69.99, 499.99), (600, 1800)),
        ],
        'Memory': [
            ('{brand} DDR4 RAM Kit {ram} ({speed})', (19.99, 229.99), (60, 250)),
            ('{brand} DDR5 RAM Kit {ram} ({speed})', (39.99, 399.99), (60, 250)),
        ],
        'Storage': [
            ('{brand} NVMe SSD {storage}', (24.99, 399.99), (40, 150)),
            ('{brand} Portable SSD {storage}', (29.99, 499.99), (80, 350)),
            ('{brand} Hard Drive {storage}', (24.99, 349.99), (350, 800)),
        ],
        'Power Supplies': [
            ('{brand} Power Supply {watt}W ({rating})', (39.99, 249.99), (1200, 3200)),
        ],
        'Cooling': [
            ('{brand} CPU Air Cooler ({socket})', (19.99, 129.99), (400, 1200)),
            ('{brand} AIO Liquid Cooler {radiator}mm', (49.99, 279.99), (1200, 2600)),
        ],
        'Cases': [
            ('{brand} Mid‑Tower PC Case ({case_color})', (39.99, 249.99), (3500, 12000)),
        ],
        'Garden Tools': [
            ('{brand} Garden Pruning Shears', (7.99, 44.99), (150, 450)),
            ('{brand} Hose {length}m with Nozzle', (9.99, 79.99), (300, 2500)),
            ('{brand} Cordless Grass Trimmer {battery}V', (39.99, 199.99), (1800, 5200)),
        ],
        'Outdoor Living': [
            ('{brand} Charcoal BBQ Grill', (39.99, 399.99), (7000, 30000)),
            ('{brand} Patio Chair Set (Set of {count})', (29.99, 349.99), (6000, 28000)),
            ('{brand} Outdoor Storage Box {capacity}L', (19.99, 249.99), (4000, 18000)),
        ],
        'Licenses': [
            ('{brand} {license_product} License ({license_term})', (9.99, 399.99), (0, 0)),
            ('{brand} {license_product} Subscription ({license_term})', (9.99, 599.99), (0, 0)),
        ],
    }

    def handle(self, *args, **kwargs):
        faker = Faker()

        with transaction.atomic():
            users = self.create_users(faker)
            self.create_addresses(users, faker)
            categories = self.create_categories()
            self.create_products(users, categories, faker)
            self.create_delivery_options()
            self.create_wishlists(users)

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

        leaf_categories = [c for c in categories if not getattr(c, 'subcategories', None) or c.subcategories.count() == 0]
        pick_categories = leaf_categories or categories

        image_bulk = []
        variant_bulk = []

        for _ in range(Command.NUMBER_OF_PRODUCTS):
            seller = random.choice(users)
            cat = random.choice(pick_categories)
            cat_name = cat.name

            brand_list = self.BRAND_SEED.get(cat_name) or self.BRAND_SEED.get('Electronics') or []
            brand = random.choice(brand_list) if brand_list else (faker.company()[:128])

            ctx = {
                'brand': brand,
                'series': random.choice(
                    ['Alpha', 'Nova', 'Pulse', 'Edge', 'Pro', 'Air', 'Max', 'Plus', 'Ultra', 'Studio']
                ),
                'storage': random.choice(['64GB', '128GB', '256GB', '512GB', '1TB']),
                'ram': random.choice(['8GB', '16GB', '32GB']),
                'cpu': random.choice(['i5', 'i7', 'Ryzen 5', 'Ryzen 7', 'M2', 'M3']),
                'cpu_series': random.choice(['Core', 'Ryzen']),
                'cpu_model': random.choice(['i3-12100F', 'i5-13400F', 'i7-14700K', 'i9-14900K', '5 5600', '5 7600X', '7 7800X3D', '9 7950X']),
                'gpu_series': random.choice(['RTX 4060', 'RTX 4070', 'RTX 4080', 'RTX 4090', 'RX 7600', 'RX 7800 XT', 'RX 7900 XT', 'RX 7900 XTX']),
                'vram': random.choice(['8', '12', '16', '24']),
                'chipset': random.choice(['B760', 'Z790', 'B650', 'X670']),
                'socket': random.choice(['LGA1700', 'AM5', 'AM4']),
                'speed': random.choice(['3200MHz', '3600MHz', '5200MHz', '6000MHz']),
                'screen': random.choice(['13.3', '14', '15.6', '16', '27']),
                'capacity': random.choice(['1.5', '1.7', '3.5', '4.5', '5.5', '6.2']),
                'size': random.choice(['24', '26', '28', '30']),
                'count': random.choice(['3', '5', '10']),
                'watt': random.choice(['20', '30', '45', '65', '100']),
                'rating': random.choice(['80+ Bronze', '80+ Gold', '80+ Platinum']),
                'radiator': random.choice(['240', '280', '360']),
                'case_color': random.choice(['Black', 'White', 'Black/Tempered Glass', 'White/Tempered Glass']),
                'length': random.choice(['10', '15', '20', '25', '30']),
                'battery': random.choice(['18', '20', '36', '40']),
                'license_product': random.choice(['Office', 'Windows 11 Pro', 'Creative Cloud', 'IntelliJ IDEA', 'AutoCAD', 'Antivirus']),
                'license_term': random.choice(['1 month', '1 year', '2 years', 'Lifetime']),
                'size_label': random.choice(['Single', 'Double', 'King', 'Queen']),
                'storage2': random.choice(['256GB SSD', '512GB SSD', '1TB SSD', '1TB HDD']),
            }
            ctx['storage'] = ctx['storage'] if random.choice([True, True, False]) else ctx['storage2']

            templates = self.PRODUCT_TEMPLATES.get(cat_name) or self.PRODUCT_TEMPLATES.get('Electronics')
            template, price_range, weight_range = random.choice(templates)
            title = template.format(**ctx)
            title = title[:255]

            base_slug = slugify(title)[:200] or f'product-{uuid.uuid4().hex[:8]}'
            slug = self._unique_product_slug(base_slug)

            price = Decimal(str(round(random.uniform(price_range[0], price_range[1]), 2)))
            compare_at = None
            if random.choice([True, False, False]):
                compare_at = Decimal(str(round(float(price) * random.uniform(1.05, 1.35), 2)))

            is_digital = cat_name in {'Licenses', 'Software'} or (
                cat_name in {'Electronics'} and random.choice([False, False, True])
            )
            delivery_charge = None if is_digital else Decimal(str(round(random.uniform(0, 9.99), 2)))
            weight_grams = None if is_digital else random.randint(weight_range[0], weight_range[1])

            product = Product.objects.create(
                seller=seller,
                title=title,
                slug=slug,
                sku=self._unique_sku(),
                brand=brand[:128],
                category=cat_name[:128],
                description=faker.paragraph(nb_sentences=5),
                currency=Currency.GBP,
                price=price,
                compareAtPrice=compare_at,
                costPrice=Decimal(str(round(float(price) * random.uniform(0.55, 0.85), 2))),
                deliveryCharge=delivery_charge,
                taxRate=Decimal('20.00') if random.choice([True, True, False]) else Decimal('0.00'),
                condition=random.choice([c[0] for c in Condition.choices]),
                stock=0 if is_digital else random.randint(0, 200),
                minOrderQuantity=1,
                maxOrderQuantity=random.choice([None, 2, 3, 5, 10]),
                stockStatus=StockStatus.IN_STOCK if random.choice([True, True, True, False]) else StockStatus.OUT_OF_STOCK,
                weightGrams=weight_grams,
                isDigital=is_digital,
                isActive=True,
                isFeatured=random.choice([True, False, False, False]),
            )

            ProductCategory.objects.create(
                product=product,
                category=cat,
                isPrimary=True,
            )

            # Ensure each product has at least 2 images, with exactly one primary.
            img_count = random.randint(2, 5)
            primary_index = random.randint(0, img_count - 1)
            for idx in range(img_count):
                # We don't need a real file; the model's getImage provides a dummy URL for display.
                image_bulk.append(
                    ProductImage(
                        product=product,
                        image=f"uploads/dummy/{product.slug}-{idx+1}.jpg",
                        altText=product.title[:255],
                        order=idx,
                        isPrimary=(idx == primary_index),
                    )
                )

            # Add some variants for physical products (sizes/colors) and for components (models).
            if not is_digital and random.choice([True, True, False]):
                variant_count = random.randint(2, 4)
                primary_price = float(product.price)
                colors = ['Black', 'White', 'Silver', 'Blue', 'Red', 'Green']
                sizes = ['S', 'M', 'L', 'XL']
                for vi in range(variant_count):
                    v_name = random.choice(['Standard', 'Pro', 'Plus', 'Max', 'Mini']) if random.choice([True, False]) else f'Option {vi+1}'
                    v_color = random.choice(colors) if random.choice([True, False]) else None
                    v_size = random.choice(sizes) if random.choice([True, False]) else None
                    v_price = Decimal(str(round(primary_price * random.uniform(0.95, 1.25), 2))) if random.choice([True, True, False]) else None
                    variant_bulk.append(
                        ProductVariant(
                            product=product,
                            name=v_name,
                            sku=f'VAR-{uuid.uuid4().hex[:12].upper()}',
                            color=v_color,
                            size=v_size,
                            modelNumber=f'MDL-{uuid.uuid4().hex[:8].upper()}' if random.choice([True, False]) else None,
                            price=v_price,
                            stock=random.randint(0, 100),
                            weightGrams=weight_grams if random.choice([True, False]) else None,
                            isActive=True,
                        )
                    )

        ProductImage.objects.bulk_create(image_bulk, batch_size=500)
        if variant_bulk:
            ProductVariant.objects.bulk_create(variant_bulk, batch_size=500)

    def create_delivery_options(self):
        DeliveryOption.objects.get_or_create(
            name='Standard delivery',
            defaults={
                'method': DeliveryMethod.STANDARD,
                'provider': 'DemoCourier',
                'minDeliveryDays': 2,
                'maxDeliveryDays': 5,
                'basePrice': Decimal('0.00'),
                'isActive': True,
            },
        )
        DeliveryOption.objects.get_or_create(
            name='Express delivery',
            defaults={
                'method': DeliveryMethod.EXPRESS,
                'provider': 'DemoCourier',
                'minDeliveryDays': 1,
                'maxDeliveryDays': 2,
                'basePrice': Decimal('4.99'),
                'isActive': True,
            },
        )

    def create_wishlists(self, users):
        products = list(Product.objects.filter(isActive=True).order_by('?')[:80])
        if not users or not products:
            return

        for u in users:
            wl, _ = Wishlist.objects.get_or_create(
                user=u,
                isDefault=True,
                defaults={'name': 'Default', 'isDefault': True},
            )
            # Add a few items per user (unique_together will protect duplicates).
            for p in random.sample(products, k=min(len(products), random.randint(6, 14))):
                WishlistItem.objects.get_or_create(wishlist=wl, product=p, variant=None)

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
