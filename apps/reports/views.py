"""Vues Rapports."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta


@login_required
def reports_dashboard(request):
    if not request.user.can_see_prices:
        from django.shortcuts import redirect
        return redirect('dashboard')

    from apps.stock.models import StockBalance, StockMovement, Warehouse
    from apps.deliveries.models import SupplierInvoice, CustomerDelivery
    from apps.products.models import Product

    # Période (30 derniers jours par défaut)
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    main_warehouse = Warehouse.objects.filter(warehouse_type='main').first()

    # Valeur de stock
    stock_value = 0
    if main_warehouse:
        balances = StockBalance.objects.filter(warehouse=main_warehouse).select_related('product')
        stock_value = sum(b.stock_value for b in balances)

    # Achats fournisseurs (période)
    total_purchases = SupplierInvoice.objects.filter(
        status='validated',
        created_at__gte=since
    ).aggregate(total=Sum('lines__total_price_ht'))['total'] or 0

    # Nombre de BL clients (période)
    total_bl_clients = CustomerDelivery.objects.filter(
        status='valide',
        created_at__gte=since
    ).count()

    # Mouvements par type
    movements_by_type = StockMovement.objects.filter(
        created_at__gte=since
    ).values('movement_type').annotate(
        count=Count('id'),
        total_qty=Sum('quantity')
    ).order_by('-count')

    # Top produits mouvementés
    top_products = StockMovement.objects.filter(
        created_at__gte=since
    ).values('product__designation', 'product__code').annotate(
        total_qty=Sum('quantity'),
        count=Count('id')
    ).order_by('-total_qty')[:10]

    # Alertes stock
    low_stock = []
    rupture = []
    if main_warehouse:
        from apps.stock.services import get_stock_stats
        stats = get_stock_stats(main_warehouse)
        low_stock = stats['low_stock']
        rupture = stats['rupture']

    context = {
        'days': days,
        'since': since,
        'stock_value': stock_value,
        'total_purchases': total_purchases,
        'total_bl_clients': total_bl_clients,
        'movements_by_type': movements_by_type,
        'top_products': top_products,
        'low_stock': low_stock,
        'rupture': rupture,
        'show_prices': True,
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def report_stock(request):
    """Rapport stock détaillé."""
    if not request.user.can_see_prices:
        from django.shortcuts import redirect
        return redirect('dashboard')
    from apps.stock.models import StockBalance, Warehouse
    warehouse_id = request.GET.get('warehouse')
    warehouses = Warehouse.objects.filter(is_active=True)
    balances = StockBalance.objects.select_related('product', 'product__category', 'warehouse')
    if warehouse_id:
        balances = balances.filter(warehouse_id=warehouse_id)
    balances = balances.order_by('warehouse__name', 'product__category__name', 'product__designation')
    total_value = sum(b.stock_value for b in balances)
    return render(request, 'reports/stock.html', {
        'balances': balances,
        'warehouses': warehouses,
        'total_value': total_value,
        'selected_warehouse': warehouse_id,
        'show_prices': True,
    })
