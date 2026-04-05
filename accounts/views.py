from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import AddressForm
from accounts.models import Address
from core import service


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
