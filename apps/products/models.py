"""Produits — Catégories et produits."""
from django.db import models
from django.core.validators import MinValueValidator
from apps.common.models import UserStampedModel


class Category(models.Model):
    """Catégorie de produit."""
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    name = models.CharField(max_length=100, verbose_name='Nom')
    description = models.TextField(blank=True, verbose_name='Description')

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(models.TextChoices):
    PIECE = 'pce', 'Pièce'
    METRE = 'm', 'Mètre'
    KG = 'kg', 'Kilogramme'
    LITRE = 'l', 'Litre'
    BOITE = 'boite', 'Boîte'
    LOT = 'lot', 'Lot'


class Product(UserStampedModel):
    """Produit / article du catalogue."""
    code = models.CharField(max_length=50, unique=True, verbose_name='Code')
    designation = models.CharField(max_length=200, verbose_name='Désignation')
    description = models.TextField(blank=True, verbose_name='Description')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products',
        verbose_name='Catégorie'
    )
    unit = models.CharField(
        max_length=10,
        choices=Unit.choices,
        default=Unit.PIECE,
        verbose_name='Unité'
    )
    unit_price_ht = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Prix unitaire HT'
    )
    min_stock_level = models.PositiveIntegerField(
        default=5,
        verbose_name='Seuil stock minimum'
    )
    is_active = models.BooleanField(default=True, verbose_name='Actif')

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['designation']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.code} — {self.designation}'
