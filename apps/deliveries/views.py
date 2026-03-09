"""Vues Livraisons — Factures fournisseur, BL internes, BL clients."""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from apps.common.utils import generate_document_number
from .models import (
    SupplierInvoice, InternalDelivery, CustomerDelivery,
    InvoiceStatus, DeliveryStatus, CustomerDeliveryStatus,
)
from .forms import (
    SupplierInvoiceForm, SupplierInvoiceLineFormSet,
    InternalDeliveryForm, InternalDeliveryLineFormSet,
    CustomerDeliveryForm, CustomerDeliveryLineFormSet,
)


# ─── Factures Fournisseur ────────────────────────────────────────────────────

class SupplierInvoiceListView(LoginRequiredMixin, ListView):
    model = SupplierInvoice
    template_name = 'deliveries/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        qs = SupplierInvoice.objects.select_related('supplier', 'created_by').order_by('-created_at')
        status = self.request.GET.get('status')
        supplier = self.request.GET.get('supplier')
        if status:
            qs = qs.filter(status=status)
        if supplier:
            qs = qs.filter(supplier_id=supplier)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statuses'] = InvoiceStatus.choices
        from apps.suppliers.models import Supplier
        ctx['suppliers'] = Supplier.objects.filter(is_active=True)
        ctx['show_prices'] = self.request.user.can_see_prices
        return ctx


class SupplierInvoiceDetailView(LoginRequiredMixin, DetailView):
    model = SupplierInvoice
    template_name = 'deliveries/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('product').all()
        ctx['show_prices'] = self.request.user.can_see_prices
        return ctx


@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = SupplierInvoiceForm(request.POST)
        formset = SupplierInvoiceLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            if not invoice.number:
                invoice.number = generate_document_number('FF', SupplierInvoice)
            invoice.save()
            formset.instance = invoice
            formset.save()
            messages.success(request, f'Facture {invoice.number} créée.')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        number = generate_document_number('FF', SupplierInvoice)
        form = SupplierInvoiceForm(initial={'number': number})
        formset = SupplierInvoiceLineFormSet()
    return render(request, 'deliveries/invoice_form.html', {
        'form': form, 'formset': formset,
        'title': 'Nouvelle facture fournisseur',
        'show_prices': request.user.can_see_prices,
    })


@login_required
def invoice_validate(request, pk):
    invoice = get_object_or_404(SupplierInvoice, pk=pk)
    if request.method == 'POST':
        try:
            invoice.validate(user=request.user)
            messages.success(request, f'Facture {invoice.number} validée. Stock mis à jour.')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('invoice_detail', pk=pk)


# ─── BL Internes ────────────────────────────────────────────────────────────

class InternalDeliveryListView(LoginRequiredMixin, ListView):
    model = InternalDelivery
    template_name = 'deliveries/internal_list.html'
    context_object_name = 'deliveries'
    paginate_by = 20

    def get_queryset(self):
        qs = InternalDelivery.objects.select_related('technician', 'created_by').order_by('-created_at')
        status = self.request.GET.get('status')
        tech = self.request.GET.get('tech')
        user = self.request.user
        if user.is_technicien:
            qs = qs.filter(technician=user)
        elif tech:
            qs = qs.filter(technician_id=tech)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statuses'] = DeliveryStatus.choices
        from apps.users.models import User
        ctx['technicians'] = User.objects.filter(role='technicien', is_active=True)
        return ctx


class InternalDeliveryDetailView(LoginRequiredMixin, DetailView):
    model = InternalDelivery
    template_name = 'deliveries/internal_detail.html'
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('product').all()
        return ctx


@login_required
def internal_delivery_create(request):
    if request.method == 'POST':
        form = InternalDeliveryForm(request.POST)
        formset = InternalDeliveryLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            delivery = form.save(commit=False)
            delivery.created_by = request.user
            if not delivery.number:
                delivery.number = generate_document_number('BLI', InternalDelivery)
            delivery.save()
            formset.instance = delivery
            formset.save()
            messages.success(request, f'BL interne {delivery.number} créé.')
            return redirect('internal_delivery_detail', pk=delivery.pk)
    else:
        number = generate_document_number('BLI', InternalDelivery)
        form = InternalDeliveryForm(initial={'number': number})
        formset = InternalDeliveryLineFormSet()
    return render(request, 'deliveries/internal_form.html', {
        'form': form, 'formset': formset,
        'title': 'Nouveau BL interne',
    })


@login_required
def internal_delivery_send(request, pk):
    """Envoie le BL (sort du stock principal)."""
    delivery = get_object_or_404(InternalDelivery, pk=pk)
    if request.method == 'POST':
        try:
            delivery.validate_and_send(user=request.user)
            messages.success(request, f'BL {delivery.number} envoyé. Stock principal mis à jour.')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('internal_delivery_detail', pk=pk)


@login_required
def internal_delivery_receive(request, pk):
    """Technicien confirme réception."""
    delivery = get_object_or_404(InternalDelivery, pk=pk)
    user = request.user
    if not (user.is_technicien and delivery.technician == user) and not user.is_admin:
        messages.error(request, 'Vous ne pouvez pas confirmer cette réception.')
        return redirect('internal_delivery_detail', pk=pk)
    if request.method == 'POST':
        try:
            delivery.receive(user=request.user)
            messages.success(request, f'BL {delivery.number} reçu. Stock technicien mis à jour.')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('internal_delivery_detail', pk=pk)


# ─── BL Clients ─────────────────────────────────────────────────────────────

class CustomerDeliveryListView(LoginRequiredMixin, ListView):
    model = CustomerDelivery
    template_name = 'deliveries/customer_list.html'
    context_object_name = 'deliveries'
    paginate_by = 20

    def get_queryset(self):
        qs = CustomerDelivery.objects.select_related('client', 'technician', 'created_by').order_by('-delivery_date', '-created_at')
        user = self.request.user
        if user.is_technicien:
            qs = qs.filter(technician=user)
        status = self.request.GET.get('status')
        client = self.request.GET.get('client')
        if status:
            qs = qs.filter(status=status)
        if client:
            qs = qs.filter(client_id=client)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statuses'] = CustomerDeliveryStatus.choices
        from apps.clients.models import Client
        ctx['clients'] = Client.objects.filter(is_active=True)
        ctx['show_prices'] = self.request.user.can_see_prices
        return ctx


class CustomerDeliveryDetailView(LoginRequiredMixin, DetailView):
    model = CustomerDelivery
    template_name = 'deliveries/customer_detail.html'
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['lines'] = self.object.lines.select_related('product').all()
        ctx['show_prices'] = self.request.user.can_see_prices
        return ctx


@login_required
def customer_delivery_create(request):
    user = request.user
    if request.method == 'POST':
        form = CustomerDeliveryForm(request.POST, user=user)
        formset = CustomerDeliveryLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            delivery = form.save(commit=False)
            delivery.technician = user
            delivery.created_by = user
            if not delivery.number:
                delivery.number = generate_document_number('BLC', CustomerDelivery)
            delivery.save()
            formset.instance = delivery
            formset.save()
            messages.success(request, f'BL client {delivery.number} cree.')
            return redirect('customer_delivery_detail', pk=delivery.pk)
    else:
        number = generate_document_number('BLC', CustomerDelivery)
        form = CustomerDeliveryForm(
            initial={'number': number, 'delivery_date': timezone.now().date()},
            user=user,
        )
        formset = CustomerDeliveryLineFormSet()
    return render(request, 'deliveries/customer_form.html', {
        'form': form, 'formset': formset,
        'title': 'Nouveau BL client',
    })


@login_required
def customer_delivery_edit(request, pk):
    delivery = get_object_or_404(CustomerDelivery, pk=pk)
    if delivery.status != CustomerDeliveryStatus.DRAFT:
        messages.error(request, 'Seul un BL brouillon peut etre modifie.')
        return redirect('customer_delivery_detail', pk=pk)
    user = request.user
    if request.method == 'POST':
        form = CustomerDeliveryForm(request.POST, instance=delivery, user=user)
        formset = CustomerDeliveryLineFormSet(request.POST, instance=delivery)
        if form.is_valid() and formset.is_valid():
            delivery = form.save(commit=False)
            delivery.updated_by = user
            delivery.save()
            formset.save()
            messages.success(request, f'BL {delivery.number} modifie.')
            return redirect('customer_delivery_detail', pk=delivery.pk)
    else:
        form = CustomerDeliveryForm(instance=delivery, user=user)
        formset = CustomerDeliveryLineFormSet(instance=delivery)
    return render(request, 'deliveries/customer_form.html', {
        'form': form, 'formset': formset,
        'title': f'Modifier BL {delivery.number}',
        'object': delivery,
    })


@login_required
def customer_delivery_validate(request, pk):
    delivery = get_object_or_404(CustomerDelivery, pk=pk)
    if request.method == 'POST':
        try:
            delivery.validate(user=request.user)
            messages.success(request, f'BL {delivery.number} valide. Stock technicien mis a jour.')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('customer_delivery_detail', pk=pk)


# ─── Impression / PDF ────────────────────────────────────────────────────────

@login_required
def invoice_print(request, pk):
    """Page d'impression professionnelle pour une facture fournisseur."""
    invoice = get_object_or_404(
        SupplierInvoice.objects.select_related('supplier', 'created_by'),
        pk=pk
    )
    lines = invoice.lines.select_related('product', 'product__category').all()
    return render(request, 'deliveries/print/invoice_print.html', {
        'invoice': invoice,
        'lines': lines,
        'show_prices': request.user.can_see_prices,
    })


@login_required
def internal_delivery_print(request, pk):
    """Page d'impression professionnelle pour un BL interne."""
    delivery = get_object_or_404(
        InternalDelivery.objects.select_related('technician', 'created_by'),
        pk=pk
    )
    lines = delivery.lines.select_related('product', 'product__category').all()
    return render(request, 'deliveries/print/internal_print.html', {
        'delivery': delivery,
        'lines': lines,
    })


@login_required
def customer_delivery_print(request, pk):
    """Page d'impression professionnelle pour un BL client."""
    delivery = get_object_or_404(
        CustomerDelivery.objects.select_related('client', 'technician', 'created_by'),
        pk=pk
    )
    lines = delivery.lines.select_related('product', 'product__category').all()
    return render(request, 'deliveries/print/customer_print.html', {
        'delivery': delivery,
        'lines': lines,
        'show_prices': request.user.can_see_prices,
    })
