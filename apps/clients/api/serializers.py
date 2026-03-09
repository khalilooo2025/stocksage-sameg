from rest_framework import serializers
from apps.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'code', 'name', 'contact_person', 'email', 'phone', 'city', 'is_active']
