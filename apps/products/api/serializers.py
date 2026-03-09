from rest_framework import serializers
from apps.products.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'code', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'code', 'designation', 'category', 'category_name', 'unit', 'unit_price_ht', 'min_stock_level', 'is_active']
