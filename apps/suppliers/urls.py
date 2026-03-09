"""URLs Fournisseurs."""
from django.urls import path
from .views import SupplierListView, SupplierDetailView, SupplierCreateView, SupplierUpdateView, supplier_toggle_active

urlpatterns = [
    path('', SupplierListView.as_view(), name='supplier_list'),
    path('nouveau/', SupplierCreateView.as_view(), name='supplier_create'),
    path('<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('<int:pk>/modifier/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('<int:pk>/activer/', supplier_toggle_active, name='supplier_toggle_active'),
]
