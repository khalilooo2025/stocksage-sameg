"""Formulaires Inventaire."""
from django import forms
from .models import InventorySession, InventoryLine


class InventorySessionForm(forms.ModelForm):
    class Meta:
        model = InventorySession
        fields = ['number', 'warehouse', 'notes']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InventoryLineForm(forms.ModelForm):
    class Meta:
        model = InventoryLine
        fields = ['actual_qty']
        widgets = {
            'actual_qty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
