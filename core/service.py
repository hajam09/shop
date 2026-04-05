import random

from accounts.models import Address


def generateOrderNumber():
    return random.randint(1000000000, 9999999999)


def sync_primary_default(user, keep_pk):
    Address.objects.filter(user=user).exclude(pk=keep_pk).update(isPrimary=False)
