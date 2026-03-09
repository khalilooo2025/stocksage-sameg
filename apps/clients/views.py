"""Vues Clients."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Client
from .forms import ClientForm


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/list.html'
    context_object_name = 'clients'
    paginate_by = 20

    def get_queryset(self):
        qs = Client.objects.all()
        q = self.request.GET.get('q')
        active = self.request.GET.get('active')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        if active == '0':
            qs = qs.filter(is_active=False)
        else:
            qs = qs.filter(is_active=True)
        return qs.order_by('name')


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['deliveries'] = self.object.deliveries.order_by('-delivery_date')[:10]
        return ctx


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Client créé avec succès.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Nouveau client'
        ctx['action'] = 'Créer'
        return ctx


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/form.html'
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Client modifié.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Modifier le client'
        ctx['action'] = 'Enregistrer'
        return ctx


@login_required
def client_toggle_active(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.is_active = not client.is_active
    client.save(update_fields=['is_active'])
    status = 'activé' if client.is_active else 'archivé'
    messages.success(request, f'Client {status}.')
    return redirect('client_list')
