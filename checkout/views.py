from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from checkout.models import Cart, CartItem
from orders.models import Order


def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, isCheckedOut=False)
        return cart

    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(sessionKey=request.session.session_key, isCheckedOut=False)
    return cart


def cartView(request):
    cart = _get_or_create_cart(request)
    items = (
        CartItem.objects.select_related('product', 'variant')
        .filter(cart=cart)
        .order_by('-createdAt')
        .all()
    )

    if request.method == 'POST':
        selected_ids = set(request.POST.getlist('checkout_item'))
        for it in items:
            it.saveForLater = str(it.pk) not in selected_ids
        CartItem.objects.bulk_update(items, ['saveForLater'])
        messages.success(request, 'Updated checkout selection.')
        return redirect('checkout:cart')

    totals = items.aggregate(
        qty=Sum('quantity'),
        total=Sum('lineTotal'),
    )
    selected = [it for it in items if not it.saveForLater]
    selected_total = sum((it.lineTotal for it in selected), Decimal('0.00'))

    return render(
        request,
        'checkout/cart.html',
        {
            'cart': cart,
            'items': items,
            'selected_items': selected,
            'cart_qty': totals['qty'] or 0,
            'cart_total': totals['total'] or Decimal('0.00'),
            'selected_total': selected_total,
        },
    )


def cartClearView(request):
    if request.method != 'POST':
        return redirect('checkout:cart')

    cart = _get_or_create_cart(request)
    CartItem.objects.filter(cart=cart).delete()
    messages.success(request, 'Cart cleared.')
    return redirect('checkout:cart')


@login_required
def cartCheckoutView(request):
    if request.method != 'POST':
        return redirect('checkout:cart')

    cart = _get_or_create_cart(request)
    items = (
        CartItem.objects.select_related('product', 'variant')
        .filter(cart=cart, saveForLater=False)
        .all()
    )
    if not items:
        messages.error(request, 'Select at least one item to checkout.')
        return redirect('checkout:cart')

    with transaction.atomic():
        for it in items:
            Order.objects.create(
                product=it.product,
                buyer=request.user,
                currency=cart.currency,
                unitPrice=it.unitPrice,
                subtotal=it.lineTotal,
                taxAmount=Decimal('0.00'),
                shippingAmount=Decimal('0.00'),
                discountAmount=Decimal('0.00'),
                total=it.lineTotal,
                quantity=it.quantity,
                placedAt=timezone.now(),
            )
        CartItem.objects.filter(pk__in=[i.pk for i in items]).delete()

        if not CartItem.objects.filter(cart=cart).exists():
            cart.isCheckedOut = True
            cart.checkedOutAt = timezone.now()
            cart.save(update_fields=['isCheckedOut', 'checkedOutAt'])

    messages.success(request, 'Checkout completed (demo).')
    return redirect('checkout:cart')

