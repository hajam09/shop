from calendar import monthrange
from datetime import date

from django import forms
from django.forms.widgets import PasswordInput

from payments.models import PaymentMethod


def _expiry_year_choices(instance_expiration=None):
    start = date.today().year
    years = list(range(start, start + 21))
    if instance_expiration and instance_expiration.year not in years:
        years.append(instance_expiration.year)
        years.sort()
    return [(y, str(y)) for y in years]


CARD_NUMBER_MAX_DIGITS = 19
CVV_LENGTH = 3


def _group_card_number(digits: str) -> str:
    digits = ''.join(ch for ch in (digits or '') if ch.isdigit())
    return ' '.join(digits[i : i + 4] for i in range(0, len(digits), 4)).strip()


class PaymentMethodForm(forms.ModelForm):
    card_number = forms.CharField(
        label='Card number',
        # Allow spaces for display formatting; validation enforces digits-only content.
        max_length=19,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'cc-number',
                'inputmode': 'numeric',
                'data-card-number': '1',
                'title': 'Digits only',
            }
        ),
    )
    cvv = forms.CharField(
        label='CVV',
        max_length=CVV_LENGTH,
        min_length=CVV_LENGTH,
        required=False,
        help_text=f'{CVV_LENGTH}-digit security code on the back of the card.',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'autocomplete': 'cc-csc',
                'inputmode': 'numeric',
                'maxlength': str(CVV_LENGTH),
                'data-cvv': '1',
                'title': f'{CVV_LENGTH} digits only',
            }
        ),
    )
    expiry_month = forms.TypedChoiceField(
        label='Expiry month',
        coerce=int,
        choices=[(m, f'{m:02d}') for m in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    expiry_year = forms.TypedChoiceField(
        label='Expiry year',
        coerce=int,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    isPrimary = forms.BooleanField(
        required=False,
        label='Primary',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = PaymentMethod
        fields = ('name', 'billingZip', 'isPrimary')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'cc-name'}),
            'billingZip': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'postal-code'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        exp = self.instance.expiration if self.instance.pk else None
        self.fields['expiry_year'].choices = _expiry_year_choices(exp)
        self.fields['billingZip'].required = True
        self.fields['billingZip'].label = 'Billing ZIP / postcode'

        if self.instance.pk and self.instance.expiration:
            self.fields['expiry_month'].initial = self.instance.expiration.month
            self.fields['expiry_year'].initial = self.instance.expiration.year

        if not self.instance.pk:
            self.fields['card_number'].required = True
            self.fields['cvv'].required = True
        else:
            self.fields['card_number'].help_text = (
                'Leave blank to keep the current card number on file. '
                f'If you change it, enter digits only (at most {CARD_NUMBER_MAX_DIGITS}).'
            )
            self.fields['cvv'].help_text = (
                f'Leave blank to keep the stored CVV. If you change it, enter a new {CVV_LENGTH}-digit code.'
            )
            # Show the card number on edit (decrypted), but never prefill CVV.
            try:
                self.fields['card_number'].initial = _group_card_number(self.instance.getCardNumber)
            except Exception:
                self.fields['card_number'].initial = None
            self.fields['cvv'].widget = PasswordInput(
                render_value=False,
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'cc-csc',
                    'inputmode': 'numeric',
                    'maxlength': str(CVV_LENGTH),
                    'data-cvv': '1',
                    'title': f'{CVV_LENGTH} digits only',
                },
            )

    def clean(self):
        cleaned = super().clean()
        month = cleaned.get('expiry_month')
        year = cleaned.get('expiry_year')
        if month is not None and year is not None:
            last_day = monthrange(year, month)[1]
            exp = date(year, month, last_day)
            if exp < date.today():
                raise forms.ValidationError('This card appears to have expired.')
        return cleaned

    def clean_card_number(self):
        raw = (self.cleaned_data.get('card_number') or '').strip()
        if self.instance.pk:
            if not raw:
                return None
        elif not raw:
            raise forms.ValidationError('Enter a valid card number.')
        normalized = ''.join(ch for ch in raw if ch.isdigit())
        if not normalized or len(normalized) != len(raw.replace(' ', '')):
            raise forms.ValidationError('Card number must contain only digits (0–9).')
        if len(normalized) > CARD_NUMBER_MAX_DIGITS:
            raise forms.ValidationError(
                f'Card number cannot be more than {CARD_NUMBER_MAX_DIGITS} digits.'
            )
        return normalized

    def clean_cvv(self):
        raw = (self.cleaned_data.get('cvv') or '').strip()
        if self.instance.pk:
            if not raw:
                return None
        elif not raw:
            raise forms.ValidationError('Enter the CVV.')
        if not raw.isdigit():
            raise forms.ValidationError('CVV must contain only digits (0–9).')
        if len(raw) != CVV_LENGTH:
            raise forms.ValidationError(f'Enter a {CVV_LENGTH}-digit CVV.')
        return raw

    def save(self, commit=True):
        instance = super().save(commit=False)
        month = self.cleaned_data['expiry_month']
        year = self.cleaned_data['expiry_year']
        last_day = monthrange(year, month)[1]
        instance.expiration = date(year, month, last_day)

        card_number = self.cleaned_data.get('card_number')
        cvv = self.cleaned_data.get('cvv')

        if not instance.pk:
            if self.user is None:
                raise ValueError('PaymentMethodForm requires user= for new payment methods.')
            instance.user = self.user
            if not PaymentMethod.objects.filter(user_id=self.user.pk).exists():
                instance.isPrimary = True
            instance.setCardNumber(card_number)
            instance.setCvvNumber(cvv)
        else:
            if card_number:
                instance.setCardNumber(card_number)
            if cvv:
                instance.setCvvNumber(cvv)

        if commit:
            instance.save()
            if instance.isPrimary:
                PaymentMethod.objects.filter(user_id=instance.user_id).exclude(pk=instance.pk).update(
                    isPrimary=False
                )
        return instance
