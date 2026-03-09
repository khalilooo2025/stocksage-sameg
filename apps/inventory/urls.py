"""URLs Inventaire."""
from django.urls import path
from .views import InventoryListView, InventoryDetailView, inventory_create, inventory_update_line, inventory_close

urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory_list'),
    path('nouveau/', inventory_create, name='inventory_create'),
    path('<int:pk>/', InventoryDetailView.as_view(), name='inventory_detail'),
    path('<int:session_pk>/ligne/<int:line_pk>/', inventory_update_line, name='inventory_update_line'),
    path('<int:pk>/cloturer/', inventory_close, name='inventory_close'),
]
