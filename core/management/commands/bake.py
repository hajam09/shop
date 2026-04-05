import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from accounts.models import Address
from accounts.choices import Country, AddressType  # adjust import path if needed


class Command(BaseCommand):
    help = "Seed Users and Addresses (fresh DB)"

    # 🔧 GLOBAL CONFIG
    NUMBER_OF_USERS = 5
    ADDRESSES_PER_USER = 2

    def handle(self, *args, **kwargs):
        faker = Faker()

        with transaction.atomic():
            users = self.create_users(faker)
            self.create_addresses(users, faker)

        self.stdout.write(self.style.SUCCESS("Users and Addresses seeded successfully"))

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

            # Optional: set a default password (hashed)
            user.set_password("password123")

            user_bulk.append(user)

        User.objects.bulk_create(user_bulk, batch_size=500)

        # ⚠️ Important: reload users to ensure IDs are available
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

    def generate_phone(self, faker):
        """
        Ensures phone number matches your regex: ^[0-9+\-() ]+$
        """
        return faker.numerify(text="+44##########")