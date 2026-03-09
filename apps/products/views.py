"""Vues Produits et Catégories."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Category
from .forms import ProductForm, CategoryForm


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 30

    def get_queryset(self):
        qs = Product.objects.select_related('category').filter(is_active=True)
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        if q:
            qs = qs.filter(designation__icontains=q) | qs.filter(code__icontains=q)
        if category:
            qs = qs.filter(category_id=category)
        return qs.order_by('designation')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['show_prices'] = self.request.user.can_see_prices
        return ctx


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['show_prices'] = self.request.user.can_see_prices
        ctx['stock_balances'] = self.object.stock_balances.select_related('warehouse').all()
        return ctx


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Produit créé avec succès.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Nouveau produit'
        ctx['action'] = 'Créer'
        return ctx


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Produit modifié.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Modifier le produit'
        ctx['action'] = 'Enregistrer'
        return ctx


# ─── Catégories ─────────────────────────────────────────────────────────────

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie créée.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie modifiée.')
        return super().form_valid(form)
