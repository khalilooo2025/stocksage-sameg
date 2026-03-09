"""Vues Fournisseurs."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Supplier
from .forms import SupplierForm


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'suppliers/list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        qs = Supplier.objects.all()
        q = self.request.GET.get('q')
        active = self.request.GET.get('active')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        if active == '0':
            qs = qs.filter(is_active=False)
        else:
            qs = qs.filter(is_active=True)
        return qs.order_by('name')


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'suppliers/detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['invoices'] = self.object.invoices.order_by('-invoice_date')[:10]
        return ctx


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Fournisseur créé avec succès.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Nouveau fournisseur'
        ctx['action'] = 'Créer'
        return ctx


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Fournisseur modifié.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Modifier le fournisseur'
        ctx['action'] = 'Enregistrer'
        return ctx


@login_required
def supplier_toggle_active(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.is_active = not supplier.is_active
    supplier.save(update_fields=['is_active'])
    status = 'activé' if supplier.is_active else 'archivé'
    messages.success(request, f'Fournisseur {status}.')
    return redirect('supplier_list')
