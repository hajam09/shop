from django import forms

from accounts.models import Address


class AddressForm(forms.ModelForm):
    error_css_class = 'is-invalid'

    class Meta:
        model = Address
        fields = [
            'fullName',
            'phoneNumber',
            'addressLine1',
            'addressLine2',
            'addressLine3',
            'town',
            'city',
            'county',
            'state',
            'postcode',
            'country',
            'isPrimary',
            'type',
            'deliveryInstructions',
        ]
        widgets = {
            'fullName': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'name'}),
            'phoneNumber': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'tel'}),
            'addressLine1': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'address-line1'}),
            'addressLine2': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'address-line2'}),
            'addressLine3': forms.TextInput(attrs={'class': 'form-control'}),
            'town': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'address-level2'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'address-level1'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'postal-code'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'isPrimary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'deliveryInstructions': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def _strip(self, value):
        if value is None:
            return value
        s = value.strip()
        return s or None

    def clean_fullName(self):
        v = self._strip(self.cleaned_data.get('fullName'))
        if not v:
            raise forms.ValidationError('Enter the full name for this address.')
        return v

    def clean_addressLine1(self):
        v = self._strip(self.cleaned_data.get('addressLine1'))
        if not v:
            raise forms.ValidationError('Enter the first line of the address.')
        return v

    def clean_city(self):
        v = self._strip(self.cleaned_data.get('city'))
        if not v:
            raise forms.ValidationError('Enter the city or locality.')
        return v

    def clean_postcode(self):
        v = self._strip(self.cleaned_data.get('postcode'))
        if not v:
            raise forms.ValidationError('Enter the postcode or ZIP code.')
        return v

    def clean_phoneNumber(self):
        return self._strip(self.cleaned_data.get('phoneNumber'))

    def clean_addressLine2(self):
        return self._strip(self.cleaned_data.get('addressLine2'))

    def clean_addressLine3(self):
        return self._strip(self.cleaned_data.get('addressLine3'))

    def clean_town(self):
        return self._strip(self.cleaned_data.get('town'))

    def clean_county(self):
        return self._strip(self.cleaned_data.get('county'))

    def clean_state(self):
        return self._strip(self.cleaned_data.get('state'))

    def clean_deliveryInstructions(self):
        return self._strip(self.cleaned_data.get('deliveryInstructions'))
