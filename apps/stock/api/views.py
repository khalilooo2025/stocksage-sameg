from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from apps.stock.models import Warehouse, StockBalance, StockMovement
from .serializers import WarehouseSerializer, StockBalanceSerializer, StockMovementSerializer


class WarehouseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Warehouse.objects.filter(is_active=True)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]


class StockBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockBalance.objects.select_related('product', 'warehouse').all()
    serializer_class = StockBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        warehouse = self.request.query_params.get('warehouse')
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        user = self.request.user
        if user.is_technicien:
            qs = qs.filter(warehouse__owner=user)
        return qs


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related('product', 'warehouse', 'created_by').order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_technicien:
            qs = qs.filter(warehouse__owner=user)
        return qs[:200]
