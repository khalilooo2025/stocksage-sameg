"""URLs Stock."""
from django.urls import path
from .views import WarehouseListView, WarehouseDetailView, StockMovementListView

urlpatterns = [
    path('', WarehouseListView.as_view(), name='stock_warehouse_list'),
    path('entrepots/<int:pk>/', WarehouseDetailView.as_view(), name='stock_warehouse_detail'),
    path('mouvements/', StockMovementListView.as_view(), name='stock_movement_list'),
]
