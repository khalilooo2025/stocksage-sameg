from rest_framework import serializers
from apps.suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'code', 'name', 'contact_person', 'email', 'phone', 'city', 'is_active']
