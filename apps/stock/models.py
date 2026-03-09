"""Stock — Entrepôts, soldes et mouvements."""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.common.models import TimeStampedModel


class WarehouseType(models.TextChoices):
    MAIN = 'main', 'Stock Principal'
    TECHNICIEN = 'technicien', 'Stock Technicien'


class Warehouse(models.Model):
    """Entrepôt / dépôt de stock."""
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    name = models.CharField(max_length=100, verbose_name='Nom')
    warehouse_type = models.CharField(
        max_length=20,
        choices=WarehouseType.choices,
        default=WarehouseType.MAIN,
        verbose_name='Type'
    )
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='warehouse',
        verbose_name='Technicien propriétaire'
    )
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Entrepôt'
        verbose_name_plural = 'Entrepôts'
        ordering = ['warehouse_type', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_warehouse_type_display()})'


class StockBalance(models.Model):
    """Solde stock par entrepôt et produit."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='balances',
        verbose_name='Entrepôt'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stock_balances',
        verbose_name='Produit'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name='Quantité'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solde stock'
        verbose_name_plural = 'Soldes stock'
        unique_together = [('warehouse', 'product')]
        ordering = ['product__designation']

    def __str__(self):
        return f'{self.product.designation} — {self.warehouse.name}: {self.quantity}'

    @property
    def is_low(self):
        return 0 < self.quantity <= self.product.min_stock_level

    @property
    def is_rupture(self):
        return self.quantity <= 0

    @property
    def stock_value(self):
        return self.quantity * self.product.unit_price_ht


class MovementType(models.TextChoices):
    ENTREE_FOURNISSEUR = 'entree_fournisseur', 'Entrée fournisseur'
    SORTIE_TECHNICIEN = 'sortie_technicien', 'Sortie vers technicien'
    RETOUR_TECHNICIEN = 'retour_technicien', 'Retour technicien'
    TRANSFERT_ENVOI = 'transfert_envoi', 'Transfert (envoi)'
    TRANSFERT_RECEPTION = 'transfert_reception', 'Transfert (réception)'
    INVENTAIRE_PLUS = 'inventaire_plus', 'Régularisation inventaire (+)'
    INVENTAIRE_MOINS = 'inventaire_moins', 'Régularisation inventaire (-)'
    SORTIE_CLIENT = 'sortie_client', 'Sortie client (BL)'
    AUTRE = 'autre', 'Autre'


class StockMovement(TimeStampedModel):
    """Mouvement de stock (historique complet)."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Entrepôt'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Produit'
    )
    movement_type = models.CharField(
        max_length=30,
        choices=MovementType.choices,
        verbose_name='Type de mouvement'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Quantité'
    )
    # + pour entrée, - pour sortie
    direction = models.SmallIntegerField(
        choices=[(1, 'Entrée'), (-1, 'Sortie')],
        default=1,
        verbose_name='Direction'
    )
    reference = models.CharField(max_length=50, blank=True, verbose_name='Référence document')
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_movements',
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['warehouse', 'product']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        direction = '+' if self.direction == 1 else '-'
        return f'{self.get_movement_type_display()} {direction}{self.quantity} × {self.product.designation}'

    @property
    def net_quantity(self):
        return self.quantity * self.direction
