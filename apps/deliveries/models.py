"""Livraisons — Factures fournisseur, BL internes, BL clients."""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.common.models import UserStampedModel


# ─── Facture Fournisseur ─────────────────────────────────────────────────────

class InvoiceStatus(models.TextChoices):
    DRAFT = 'draft', 'Brouillon'
    VALIDATED = 'validated', 'Validée'
    CANCELLED = 'cancelled', 'Annulée'


class SupplierInvoice(UserStampedModel):
    """Facture fournisseur (entrée stock principal)."""
    number = models.CharField(max_length=30, unique=True, verbose_name='Numéro')
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Fournisseur'
    )
    invoice_date = models.DateField(verbose_name='Date facture')
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        verbose_name='Statut'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')

    class Meta:
        verbose_name = 'Facture fournisseur'
        verbose_name_plural = 'Factures fournisseur'
        ordering = ['-invoice_date', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['supplier']),
        ]

    def __str__(self):
        return f'{self.number} — {self.supplier.name}'

    @property
    def total_ht(self):
        return sum(line.total_price_ht for line in self.lines.all())

    def validate(self, user=None):
        """Valide la facture et enregistre les entrées en stock."""
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError('Seule une facture brouillon peut être validée.')
        from apps.stock.models import Warehouse, StockBalance, StockMovement, MovementType
        main_warehouse = Warehouse.objects.filter(warehouse_type='main').first()
        if not main_warehouse:
            raise ValueError('Aucun entrepôt principal configuré.')
        for line in self.lines.select_related('product').all():
            balance, _ = StockBalance.objects.get_or_create(
                warehouse=main_warehouse,
                product=line.product,
                defaults={'quantity': 0}
            )
            balance.quantity += line.quantity
            balance.save(update_fields=['quantity', 'updated_at'])
            StockMovement.objects.create(
                warehouse=main_warehouse,
                product=line.product,
                movement_type=MovementType.ENTREE_FOURNISSEUR,
                quantity=line.quantity,
                direction=1,
                reference=self.number,
                notes=f'Facture {self.number}',
                created_by=user,
            )
        self.status = InvoiceStatus.VALIDATED
        self.save(update_fields=['status'])


class SupplierInvoiceLine(models.Model):
    """Ligne de facture fournisseur."""
    invoice = models.ForeignKey(
        SupplierInvoice,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Facture'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='invoice_lines',
        verbose_name='Produit'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Quantité'
    )
    unit_price_ht = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Prix unitaire HT'
    )
    total_price_ht = models.DecimalField(
        max_digits=14, decimal_places=2,
        verbose_name='Total HT'
    )

    class Meta:
        verbose_name = 'Ligne facture'
        verbose_name_plural = 'Lignes facture'

    def save(self, *args, **kwargs):
        self.total_price_ht = self.quantity * self.unit_price_ht
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.designation} × {self.quantity}'


# ─── Bon de Livraison Interne ────────────────────────────────────────────────

class DeliveryStatus(models.TextChoices):
    DRAFT = 'draft', 'Brouillon'
    VALIDE = 'valide', 'Validé'
    EN_TRANSIT = 'en_transit', 'En transit'
    RECU = 'recu', 'Reçu'
    ANNULE = 'annule', 'Annulé'


class InternalDelivery(UserStampedModel):
    """Bon de livraison interne (stock principal → technicien)."""
    number = models.CharField(max_length=30, unique=True, verbose_name='Numéro')
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='received_deliveries',
        limit_choices_to={'role': 'technicien'},
        verbose_name='Technicien destinataire'
    )
    delivery_date = models.DateField(null=True, blank=True, verbose_name='Date livraison')
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.DRAFT,
        verbose_name='Statut'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')

    class Meta:
        verbose_name = 'BL Interne'
        verbose_name_plural = 'BL Internes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['technician']),
        ]

    def __str__(self):
        return f'{self.number} → {self.technician.full_name}'

    def validate_and_send(self, user=None):
        """Valide et met en transit : sort du stock principal, stock tech pas encore mis à jour."""
        if self.status not in [DeliveryStatus.DRAFT, DeliveryStatus.VALIDE]:
            raise ValueError('Statut invalide pour cet envoi.')
        from apps.stock.models import Warehouse, StockBalance, StockMovement, MovementType
        main_warehouse = Warehouse.objects.filter(warehouse_type='main').first()
        if not main_warehouse:
            raise ValueError('Aucun entrepôt principal configuré.')
        for line in self.lines.select_related('product').all():
            balance = StockBalance.objects.filter(
                warehouse=main_warehouse, product=line.product
            ).first()
            if not balance or balance.quantity < line.quantity:
                raise ValueError(f'Stock insuffisant pour {line.product.designation}.')
            balance.quantity -= line.quantity
            balance.save(update_fields=['quantity', 'updated_at'])
            StockMovement.objects.create(
                warehouse=main_warehouse,
                product=line.product,
                movement_type=MovementType.SORTIE_TECHNICIEN,
                quantity=line.quantity,
                direction=-1,
                reference=self.number,
                notes=f'BL {self.number} vers {self.technician.full_name}',
                created_by=user,
            )
        self.status = DeliveryStatus.EN_TRANSIT
        self.save(update_fields=['status'])

    def receive(self, user=None):
        """Technicien confirme réception : ajoute au stock technicien."""
        if self.status != DeliveryStatus.EN_TRANSIT:
            raise ValueError('Le BL doit être en transit pour être reçu.')
        from apps.stock.models import Warehouse, StockBalance, StockMovement, MovementType
        tech_warehouse = Warehouse.objects.filter(
            warehouse_type='technicien', owner=self.technician
        ).first()
        if not tech_warehouse:
            from apps.stock.models import Warehouse as W
            tech_warehouse = W.objects.create(
                warehouse_type='technicien',
                owner=self.technician,
                name=f'Stock de {self.technician.full_name}',
                code=f'TECH-{self.technician.pk}',
            )
        for line in self.lines.select_related('product').all():
            balance, _ = StockBalance.objects.get_or_create(
                warehouse=tech_warehouse,
                product=line.product,
                defaults={'quantity': 0}
            )
            balance.quantity += line.quantity
            balance.save(update_fields=['quantity', 'updated_at'])
            StockMovement.objects.create(
                warehouse=tech_warehouse,
                product=line.product,
                movement_type=MovementType.TRANSFERT_RECEPTION,
                quantity=line.quantity,
                direction=1,
                reference=self.number,
                notes=f'Réception BL {self.number}',
                created_by=user,
            )
        self.status = DeliveryStatus.RECU
        self.save(update_fields=['status'])


class InternalDeliveryLine(models.Model):
    """Ligne de BL interne."""
    delivery = models.ForeignKey(
        InternalDelivery,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='BL'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='internal_delivery_lines',
        verbose_name='Produit'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Quantité'
    )

    class Meta:
        verbose_name = 'Ligne BL interne'
        verbose_name_plural = 'Lignes BL internes'

    def __str__(self):
        return f'{self.product.designation} × {self.quantity}'


# ─── Bon de Livraison Client ─────────────────────────────────────────────────

class CustomerDeliveryStatus(models.TextChoices):
    DRAFT = 'draft', 'Brouillon'
    VALIDE = 'valide', 'Validé'
    FACTURE = 'facture', 'Facturé'


class CustomerDelivery(UserStampedModel):
    """Bon de livraison client (technicien → client)."""
    number = models.CharField(max_length=30, unique=True, verbose_name='Numéro')
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='customer_deliveries',
        verbose_name='Technicien'
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='deliveries',
        verbose_name='Client'
    )
    delivery_date = models.DateField(verbose_name='Date BL')
    order_number = models.CharField(
        max_length=50, blank=True, verbose_name='N° Ordre client'
    )
    intervention_details = models.TextField(
        blank=True, verbose_name='Détails intervention'
    )
    status = models.CharField(
        max_length=20,
        choices=CustomerDeliveryStatus.choices,
        default=CustomerDeliveryStatus.DRAFT,
        verbose_name='Statut'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')

    class Meta:
        verbose_name = 'BL Client'
        verbose_name_plural = 'BL Clients'
        ordering = ['-delivery_date', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['technician']),
            models.Index(fields=['client']),
        ]

    def __str__(self):
        return f'{self.number} — {self.client.name}'

    def validate(self, user=None):
        """Valide le BL : sort du stock technicien."""
        if self.status != CustomerDeliveryStatus.DRAFT:
            raise ValueError('Seul un BL brouillon peut être validé.')
        from apps.stock.models import Warehouse, StockBalance, StockMovement, MovementType
        tech_warehouse = Warehouse.objects.filter(
            warehouse_type='technicien', owner=self.technician
        ).first()
        if not tech_warehouse:
            raise ValueError('Aucun stock technicien trouvé.')
        for line in self.lines.select_related('product').all():
            balance = StockBalance.objects.filter(
                warehouse=tech_warehouse, product=line.product
            ).first()
            if not balance or balance.quantity < line.quantity:
                raise ValueError(f'Stock insuffisant pour {line.product.designation}.')
            balance.quantity -= line.quantity
            balance.save(update_fields=['quantity', 'updated_at'])
            StockMovement.objects.create(
                warehouse=tech_warehouse,
                product=line.product,
                movement_type=MovementType.SORTIE_CLIENT,
                quantity=line.quantity,
                direction=-1,
                reference=self.number,
                notes=f'BL client {self.number} — {self.client.name}',
                created_by=user,
            )
        self.status = CustomerDeliveryStatus.VALIDE
        self.save(update_fields=['status'])


class CustomerDeliveryLine(models.Model):
    """Ligne de BL client."""
    delivery = models.ForeignKey(
        CustomerDelivery,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='BL'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='customer_delivery_lines',
        verbose_name='Produit'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Quantité'
    )

    class Meta:
        verbose_name = 'Ligne BL client'
        verbose_name_plural = 'Lignes BL client'

    def __str__(self):
        return f'{self.product.designation} × {self.quantity}'
