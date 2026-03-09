"""Vues Stock — Entrepôts, soldes, mouvements."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from .models import Warehouse, StockBalance, StockMovement
from apps.users.permissions import MagasinierRequiredMixin


class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'stock/warehouse_list.html'
    context_object_name = 'warehouses'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager or user.is_magasinier:
            return Warehouse.objects.filter(is_active=True).select_related('owner')
        # Technicien ne voit que son propre entrepôt
        return Warehouse.objects.filter(owner=user, is_active=True)


class WarehouseDetailView(LoginRequiredMixin, DetailView):
    model = Warehouse
    template_name = 'stock/warehouse_detail.html'
    context_object_name = 'warehouse'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        balances = StockBalance.objects.filter(
            warehouse=self.object
        ).select_related('product', 'product__category').order_by('product__designation')

        q = self.request.GET.get('q')
        if q:
            balances = balances.filter(
                Q(product__designation__icontains=q) | Q(product__code__icontains=q)
            )

        from .services import get_stock_stats
        stats = get_stock_stats(self.object)
        ctx['balances'] = balances
        ctx['stats'] = stats
        ctx['show_prices'] = self.request.user.can_see_prices
        ctx['q'] = q or ''
        return ctx


class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'stock/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 30

    def get_queryset(self):
        user = self.request.user
        qs = StockMovement.objects.select_related('product', 'warehouse', 'created_by').order_by('-created_at')
        if user.is_technicien:
            # Technicien ne voit que son propre stock
            warehouse = Warehouse.objects.filter(owner=user).first()
            if warehouse:
                qs = qs.filter(warehouse=warehouse)
            else:
                qs = qs.none()

        warehouse_id = self.request.GET.get('warehouse')
        product_id = self.request.GET.get('product')
        mv_type = self.request.GET.get('type')

        if warehouse_id:
            qs = qs.filter(warehouse_id=warehouse_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        if mv_type:
            qs = qs.filter(movement_type=mv_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['warehouses'] = Warehouse.objects.filter(is_active=True)
        ctx['movement_types'] = StockMovement.movement_type.field.choices
        return ctx
