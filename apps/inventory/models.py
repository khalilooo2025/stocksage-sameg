"""Inventaire — Sessions et lignes d'inventaire."""
from django.db import models
from django.conf import settings
from apps.common.models import UserStampedModel


class InventoryStatus(models.TextChoices):
    OPEN = 'open', 'En cours'
    CLOSED = 'closed', 'Clôturé'


class InventorySession(UserStampedModel):
    """Session d'inventaire (comptage physique)."""
    number = models.CharField(max_length=30, unique=True, verbose_name='Numéro')
    warehouse = models.ForeignKey(
        'stock.Warehouse',
        on_delete=models.PROTECT,
        related_name='inventory_sessions',
        verbose_name='Entrepôt'
    )
    status = models.CharField(
        max_length=10,
        choices=InventoryStatus.choices,
        default=InventoryStatus.OPEN,
        verbose_name='Statut'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Clôturé le')

    class Meta:
        verbose_name = 'Inventaire'
        verbose_name_plural = 'Inventaires'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} — {self.warehouse.name}'

    def close(self, user=None):
        """Clôture l'inventaire et applique les régularisations."""
        if self.status != InventoryStatus.OPEN:
            raise ValueError('Inventaire déjà clôturé.')
        from django.utils import timezone
        from apps.stock.models import StockBalance, StockMovement, MovementType
        for line in self.lines.select_related('product').all():
            diff = line.actual_qty - line.theoretical_qty
            if diff == 0:
                continue
            balance, _ = StockBalance.objects.get_or_create(
                warehouse=self.warehouse,
                product=line.product,
                defaults={'quantity': 0}
            )
            balance.quantity = line.actual_qty
            balance.save(update_fields=['quantity', 'updated_at'])
            if diff > 0:
                mv_type = MovementType.INVENTAIRE_PLUS
                direction = 1
                qty = diff
            else:
                mv_type = MovementType.INVENTAIRE_MOINS
                direction = -1
                qty = -diff
            StockMovement.objects.create(
                warehouse=self.warehouse,
                product=line.product,
                movement_type=mv_type,
                quantity=qty,
                direction=direction,
                reference=self.number,
                notes=f'Régularisation inventaire {self.number}',
                created_by=user,
            )
        self.status = InventoryStatus.CLOSED
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at'])


class InventoryLine(models.Model):
    """Ligne d'inventaire (produit compté)."""
    session = models.ForeignKey(
        InventorySession,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Inventaire'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='inventory_lines',
        verbose_name='Produit'
    )
    theoretical_qty = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name='Quantité théorique'
    )
    actual_qty = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0,
        verbose_name='Quantité réelle'
    )

    class Meta:
        verbose_name = 'Ligne inventaire'
        verbose_name_plural = 'Lignes inventaire'
        unique_together = [('session', 'product')]

    def __str__(self):
        return f'{self.product.designation}: théo={self.theoretical_qty} réel={self.actual_qty}'

    @property
    def difference(self):
        return self.actual_qty - self.theoretical_qty
