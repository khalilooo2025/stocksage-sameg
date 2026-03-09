"""Formulaires Livraisons."""
from django import forms
from django.forms import inlineformset_factory
from .models import (
    SupplierInvoice, SupplierInvoiceLine,
    InternalDelivery, InternalDeliveryLine,
    CustomerDelivery, CustomerDeliveryLine,
)


class SupplierInvoiceForm(forms.ModelForm):
    class Meta:
        model = SupplierInvoice
        fields = ['number', 'supplier', 'invoice_date', 'notes']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class SupplierInvoiceLineForm(forms.ModelForm):
    class Meta:
        model = SupplierInvoiceLine
        fields = ['product', 'quantity', 'unit_price_ht']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


SupplierInvoiceLineFormSet = inlineformset_factory(
    SupplierInvoice, SupplierInvoiceLine,
    form=SupplierInvoiceLineForm,
    extra=3, can_delete=True, min_num=1,
)


class InternalDeliveryForm(forms.ModelForm):
    class Meta:
        model = InternalDelivery
        fields = ['number', 'technician', 'delivery_date', 'notes']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'technician': forms.Select(attrs={'class': 'form-select'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.users.models import User
        self.fields['technician'].queryset = User.objects.filter(role='technicien', is_active=True)


class InternalDeliveryLineForm(forms.ModelForm):
    class Meta:
        model = InternalDeliveryLine
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


InternalDeliveryLineFormSet = inlineformset_factory(
    InternalDelivery, InternalDeliveryLine,
    form=InternalDeliveryLineForm,
    extra=3, can_delete=True, min_num=1,
)


class CustomerDeliveryForm(forms.ModelForm):
    class Meta:
        model = CustomerDelivery
        fields = ['number', 'client', 'delivery_date', 'order_number', 'intervention_details', 'notes']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "N d'ordre du client"}),
            'intervention_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': "Details de l'intervention"}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user
        # order_number obligatoire pour les techniciens
        if user and user.is_technicien:
            self.fields['order_number'].required = True

    def clean_order_number(self):
        value = self.cleaned_data.get('order_number', '').strip()
        if self._user and self._user.is_technicien and not value:
            raise forms.ValidationError("Le N d'Ordre est obligatoire pour les techniciens.")
        return value


class CustomerDeliveryLineForm(forms.ModelForm):
    class Meta:
        model = CustomerDeliveryLine
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


CustomerDeliveryLineFormSet = inlineformset_factory(
    CustomerDelivery, CustomerDeliveryLine,
    form=CustomerDeliveryLineForm,
    extra=3, can_delete=True, min_num=1,
)
