from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import AddressForm
from accounts.models import Address, Wishlist, WishlistItem
from catalog.models import Product
from core import service


def loginView(request):
    pass


def logoutView(request):
    pass


def registerView(request):
    pass


def activateAccountView(request, encodedId, token):
    pass


def forgotPasswordView(request):
    pass


def setPasswordView(request, encodedId, token):
    pass


def addressView(request):
    pass


@login_required
def address_book(request):
    addresses = Address.objects.filter(user=request.user).order_by('-isPrimary', '-updatedAt', '-createdAt')
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                address = form.save(commit=False)
                address.user = request.user
                address.save()
                if address.isPrimary:
                    service.sync_primary_default(request.user, address.pk)
            messages.success(request, 'Your new address has been saved.')
            return redirect('accounts:address_book')
    else:
        form = AddressForm()

    context = {
        'addresses': addresses,
        'form': form
    }
    return render(request, 'accounts/address_book.html', context)


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            with transaction.atomic():
                updated = form.save()
                if updated.isPrimary:
                    service.sync_primary_default(request.user, updated.pk)
            messages.success(request, 'Address updated.')
            return redirect('accounts:address_book')
    else:
        form = AddressForm(instance=address)

    context = {
        'form': form,
        'address': address
    }

    return render(request, 'accounts/address_edit.html', context)


@login_required
@require_POST
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Address removed.')
    return redirect('accounts:address_book')


@login_required
def wishlistView(request):
    wishlist, _ = Wishlist.objects.get_or_create(
        user=request.user,
        isDefault=True,
        defaults={'name': 'Default', 'isDefault': True},
    )
    items = (
        WishlistItem.objects.select_related('product', 'variant')
        .filter(wishlist=wishlist)
        .order_by('-createdAt')
        .all()
    )
    return render(
        request,
        'accounts/wishlist.html',
        {
            'wishlist': wishlist,
            'items': items,
        },
    )


@login_required
@require_POST
def wishlistAddView(request, slug):
    product = get_object_or_404(Product, slug=slug, isActive=True)
    wishlist, _ = Wishlist.objects.get_or_create(
        user=request.user,
        isDefault=True,
        defaults={'name': 'Default', 'isDefault': True},
    )
    WishlistItem.objects.get_or_create(wishlist=wishlist, product=product, variant=None)
    messages.success(request, 'Added to wishlist.')
    return redirect(request.POST.get('next') or 'accounts:wishlist')


@login_required
@require_POST
def wishlistRemoveView(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist = get_object_or_404(Wishlist, user=request.user, isDefault=True)
    WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
    messages.success(request, 'Removed from wishlist.')
    return redirect(request.POST.get('next') or 'accounts:wishlist')


@login_required
@require_POST
def wishlistClearView(request):
    wishlist = get_object_or_404(Wishlist, user=request.user, isDefault=True)
    WishlistItem.objects.filter(wishlist=wishlist).delete()
    messages.success(request, 'Wishlist cleared.')
    return redirect('accounts:wishlist')
