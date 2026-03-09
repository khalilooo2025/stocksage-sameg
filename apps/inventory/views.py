"""Vues Inventaire."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from apps.common.utils import generate_document_number
from apps.stock.models import Warehouse, StockBalance
from .models import InventorySession, InventoryLine, InventoryStatus
from .forms import InventorySessionForm


class InventoryListView(LoginRequiredMixin, ListView):
    model = InventorySession
    template_name = 'inventory/list.html'
    context_object_name = 'sessions'
    paginate_by = 20

    def get_queryset(self):
        qs = InventorySession.objects.select_related('warehouse', 'created_by').order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statuses'] = InventoryStatus.choices
        return ctx


class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = InventorySession
    template_name = 'inventory/detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('product', 'product__category').order_by('product__designation')
        ctx['show_prices'] = self.request.user.can_see_prices
        return ctx


@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventorySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.created_by = request.user
            if not session.number:
                session.number = generate_document_number('INV', InventorySession)
            session.save()
            # Pré-remplir les lignes avec les soldes actuels
            warehouse = session.warehouse
            balances = StockBalance.objects.filter(warehouse=warehouse).select_related('product')
            lines = []
            for balance in balances:
                lines.append(InventoryLine(
                    session=session,
                    product=balance.product,
                    theoretical_qty=balance.quantity,
                    actual_qty=balance.quantity,
                ))
            InventoryLine.objects.bulk_create(lines)
            messages.success(request, f'Inventaire {session.number} créé avec {len(lines)} articles.')
            return redirect('inventory_detail', pk=session.pk)
    else:
        number = generate_document_number('INV', InventorySession)
        form = InventorySessionForm(initial={'number': number})
    return render(request, 'inventory/form.html', {
        'form': form,
        'title': 'Nouvel inventaire',
    })


@login_required
def inventory_update_line(request, session_pk, line_pk):
    """Mise à jour de la quantité réelle d'une ligne."""
    session = get_object_or_404(InventorySession, pk=session_pk)
    line = get_object_or_404(InventoryLine, pk=line_pk, session=session)
    if session.status == InventoryStatus.CLOSED:
        messages.error(request, 'Inventaire clôturé, impossible de modifier.')
        return redirect('inventory_detail', pk=session_pk)
    if request.method == 'POST':
        try:
            qty = float(request.POST.get('actual_qty', 0))
            line.actual_qty = qty
            line.save(update_fields=['actual_qty'])
        except (ValueError, TypeError):
            messages.error(request, 'Quantité invalide.')
    return redirect('inventory_detail', pk=session_pk)


@login_required
def inventory_close(request, pk):
    """Clôture l'inventaire et applique les régularisations."""
    session = get_object_or_404(InventorySession, pk=pk)
    if request.method == 'POST':
        try:
            session.close(user=request.user)
            messages.success(request, f'Inventaire {session.number} clôturé. Stock mis à jour.')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('inventory_detail', pk=pk)
