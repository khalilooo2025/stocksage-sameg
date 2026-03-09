"""Fournisseurs — Modèle fournisseur."""
from django.db import models
from apps.common.models import UserStampedModel


class Supplier(UserStampedModel):
    """Fournisseur."""
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    name = models.CharField(max_length=200, verbose_name='Nom')
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='Contact')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    address = models.TextField(blank=True, verbose_name='Adresse')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ville')
    notes = models.TextField(blank=True, verbose_name='Notes')
    is_active = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.code} — {self.name}'
