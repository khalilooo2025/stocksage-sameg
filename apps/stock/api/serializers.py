from rest_framework import serializers
from apps.stock.models import Warehouse, StockBalance, StockMovement


class WarehouseSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)

    class Meta:
        model = Warehouse
        fields = ['id', 'code', 'name', 'warehouse_type', 'owner', 'owner_name', 'is_active']


class StockBalanceSerializer(serializers.ModelSerializer):
    product_code = serializers.CharField(source='product.code', read_only=True)
    product_name = serializers.CharField(source='product.designation', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    is_low = serializers.BooleanField(read_only=True)
    is_rupture = serializers.BooleanField(read_only=True)

    class Meta:
        model = StockBalance
        fields = ['id', 'warehouse', 'warehouse_name', 'product', 'product_code', 'product_name', 'quantity', 'is_low', 'is_rupture']


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.designation', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'warehouse', 'warehouse_name', 'product', 'product_name', 'movement_type', 'quantity', 'direction', 'reference', 'notes', 'created_by', 'created_by_name', 'created_at']
