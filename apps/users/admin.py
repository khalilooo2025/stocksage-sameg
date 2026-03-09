from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'email', 'role', 'phone', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations métier', {
            'fields': ('role', 'phone', 'avatar'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations métier', {
            'fields': ('role', 'phone', 'first_name', 'last_name', 'email'),
        }),
    )
