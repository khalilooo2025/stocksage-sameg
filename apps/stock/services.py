"""Services stock — logique métier réutilisable."""
from django.db.models import Sum
from .models import StockBalance, Warehouse


def get_stock_stats(warehouse: Warehouse) -> dict:
    """Retourne les statistiques de stock pour un entrepôt donné."""
    balances = StockBalance.objects.filter(
        warehouse=warehouse
    ).select_related('product', 'product__category')

    total_products = balances.filter(quantity__gt=0).count()
    total_value = sum(b.stock_value for b in balances if b.quantity > 0)
    low_stock = [b for b in balances if b.is_low]
    rupture = [b for b in balances if b.is_rupture]

    return {
        'total_products': total_products,
        'total_value': total_value,
        'low_stock': low_stock,
        'rupture': rupture,
        'low_stock_count': len(low_stock),
        'rupture_count': len(rupture),
    }


def adjust_stock(warehouse: Warehouse, product, quantity_delta, movement_type, reference='', notes='', user=None):
    """
    Ajuste le stock d'un produit dans un entrepôt.
    quantity_delta positif = entrée, négatif = sortie.
    """
    from .models import StockMovement
    balance, _ = StockBalance.objects.get_or_create(
        warehouse=warehouse,
        product=product,
        defaults={'quantity': 0}
    )
    balance.quantity += quantity_delta
    balance.save(update_fields=['quantity', 'updated_at'])

    direction = 1 if quantity_delta >= 0 else -1
    StockMovement.objects.create(
        warehouse=warehouse,
        product=product,
        movement_type=movement_type,
        quantity=abs(quantity_delta),
        direction=direction,
        reference=reference,
        notes=notes,
        created_by=user,
    )
    return balance
