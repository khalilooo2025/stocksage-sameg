"""URLs du dashboard."""
from django.urls import path
from apps.users.views.dashboard import (
    dashboard_redirect,
    dashboard_admin,
    dashboard_manager,
    dashboard_magasinier,
    dashboard_technicien,
)

urlpatterns = [
    path('', dashboard_redirect, name='dashboard'),
    path('admin/', dashboard_admin, name='dashboard_admin'),
    path('manager/', dashboard_manager, name='dashboard_manager'),
    path('magasinier/', dashboard_magasinier, name='dashboard_magasinier'),
    path('technicien/', dashboard_technicien, name='dashboard_technicien'),
]
