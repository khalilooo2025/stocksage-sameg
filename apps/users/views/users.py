"""Gestion des utilisateurs (admin seulement)."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from ..models import User
from ..forms import UserCreateForm, UserUpdateForm
from ..permissions import AdminRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'users/list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.order_by('role', 'last_name')
        role = self.request.GET.get('role')
        search = self.request.GET.get('q')
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(
                username__icontains=search
            ) | qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            ) | qs.filter(
                email__icontains=search
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['roles'] = User.role.field.choices
        return ctx


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'users/form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Créer le dépôt technicien automatiquement
        if form.instance.role == 'technicien':
            from apps.stock.models import Warehouse
            Warehouse.objects.get_or_create(
                warehouse_type='technicien',
                owner=form.instance,
                defaults={
                    'name': f'Stock de {form.instance.full_name}',
                    'code': f'TECH-{form.instance.pk}',
                }
            )
        messages.success(self.request, 'Utilisateur créé avec succès.')
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Créer un utilisateur'
        ctx['action'] = 'Créer'
        return ctx


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/form.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Utilisateur modifié.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Modifier l\'utilisateur'
        ctx['action'] = 'Enregistrer'
        return ctx


@login_required
def user_toggle_active(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Accès refusé.')
        return redirect('dashboard')

    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'Vous ne pouvez pas désactiver votre propre compte.')
        return redirect('user_list')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    status = 'activé' if user.is_active else 'désactivé'
    messages.success(request, f'Utilisateur {status}.')
    return redirect('user_list')
