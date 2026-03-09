"""
Permissions centralisées par rôle.
Utilisées dans les vues Django et les APIViews DRF.
"""
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from rest_framework.permissions import BasePermission


# ============================================================
# Permissions DRF (API)
# ============================================================

class IsAdmin(BasePermission):
    """Seul l'administrateur peut accéder."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsManagerOrAdmin(BasePermission):
    """Manager ou Administrateur."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_manager
        )


class IsMagasinierOrAdmin(BasePermission):
    """Magasinier ou Administrateur."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_magasinier
        )


class IsTechnicien(BasePermission):
    """Technicien uniquement."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_technicien


class IsNotTechnicien(BasePermission):
    """Tout le monde sauf technicien."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_technicien


class CanSeePrices(BasePermission):
    """Permission de voir les prix — JAMAIS le technicien."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_see_prices


class IsStockManager(BasePermission):
    """Peut gérer le stock principal (admin ou magasinier)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_magasinier
        )


class CanReadStock(BasePermission):
    """Peut consulter le stock (admin, manager, magasinier)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or
            request.user.is_manager or
            request.user.is_magasinier
        )


# ============================================================
# Mixins Django Views (templates)
# ============================================================

class RoleRequiredMixin(AccessMixin):
    """Mixin de base pour vérification de rôle."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allowed_roles and request.user.role not in self.allowed_roles and not request.user.is_admin:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin:
            return redirect('dashboard')
        return super(RoleRequiredMixin, self).dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['manager', 'admin']


class MagasinierRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['magasinier', 'admin']


class TechnicienRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['technicien']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_technicien or request.user.is_admin):
            return redirect('dashboard')
        return super(RoleRequiredMixin, self).dispatch(request, *args, **kwargs)


class NoPriceMixin:
    """Mixin qui marque une vue comme sans prix."""
    show_prices = False
