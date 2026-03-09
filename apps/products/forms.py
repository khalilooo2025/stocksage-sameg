"""Formulaires Produits."""
from django import forms
from .models import Product, Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'designation', 'description', 'category', 'unit', 'unit_price_ht', 'min_stock_level', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'unit_price_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
