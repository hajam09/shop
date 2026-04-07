from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from payments.forms import PaymentMethodForm
from payments.models import PaymentMethod


@login_required
def paymentMethodView(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method created.')
            return redirect('payments:payment-method-view')
    else:
        form = PaymentMethodForm(user=request.user)

    methods = (
        PaymentMethod.objects.filter(user=request.user)
        .order_by('-isPrimary', '-createdAt')
        .all()
    )

    return render(
        request,
        'payments/payment_method_view.html',
        {
            'form': form,
            'payment_methods': methods,
        },
    )


@login_required
def paymentMethodEditView(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment method updated.')
            return redirect('payments:payment-method-view')
    else:
        form = PaymentMethodForm(instance=payment_method, user=request.user)

    return render(
        request,
        'payments/payment_method_edit.html',
        {
            'form': form,
            'payment_method': payment_method,
        },
    )


@login_required
def paymentMethodDeleteView(request, pk):
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)

    if request.method == 'POST':
        label = payment_method.name
        payment_method.delete()
        messages.success(request, f'Payment method “{label}” was deleted.')
        return redirect('payments:payment-method-view')

    return render(
        request,
        'payments/payment_method_confirm_delete.html',
        {
            'payment_method': payment_method,
        },
    )
