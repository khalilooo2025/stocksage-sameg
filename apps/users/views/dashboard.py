"""
Vues Dashboard par rôle.
Chaque rôle a son propre dashboard avec données pertinentes.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum, Count, Q


@login_required
def dashboard_redirect(request):
    """Redirige vers le dashboard approprié selon le rôle."""
    user = request.user
    if user.is_admin:
        return redirect('dashboard_admin')
    elif user.is_manager:
        return redirect('dashboard_manager')
    elif user.is_magasinier:
        return redirect('dashboard_magasinier')
    elif user.is_technicien:
        return redirect('dashboard_technicien')
    return redirect('dashboard_admin')


@login_required
def dashboard_admin(request):
    """Dashboard Administrateur — vue globale."""
    if not request.user.is_admin:
        return redirect('dashboard')

    from apps.clients.models import Client
    from apps.suppliers.models import Supplier
    from apps.users.models import User
    from apps.stock.models import StockBalance, Warehouse
    from apps.deliveries.models import SupplierInvoice, InternalDelivery, CustomerDelivery
    from apps.stock.models import StockMovement
    from apps.notifications.models import Notification

    # Stats globales
    total_clients = Client.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    total_users = User.objects.filter(is_active=True).count()

    # Stock principal
    main_warehouse = Warehouse.objects.filter(warehouse_type='main').first()
    stock_value = 0
    low_stock_products = []
    rupture_products = []

    if main_warehouse:
        from apps.products.models import Product
        from apps.stock.services import get_stock_stats
        stats = get_stock_stats(main_warehouse)
        stock_value = stats.get('total_value', 0)
        low_stock_products = stats.get('low_stock', [])
        rupture_products = stats.get('rupture', [])

    # Transferts
    pending_transfers = InternalDelivery.objects.filter(
        status='en_transit'
    ).count()
    pending_receipts = InternalDelivery.objects.filter(
        status='en_transit'
    ).count()

    # Documents récents
    recent_invoices = SupplierInvoice.objects.select_related(
        'supplier', 'created_by'
    ).order_by('-created_at')[:5]

    recent_deliveries = InternalDelivery.objects.select_related(
        'technician', 'created_by'
    ).order_by('-created_at')[:5]

    recent_movements = StockMovement.objects.select_related(
        'product', 'warehouse', 'created_by'
    ).order_by('-created_at')[:10]

    # Notifications non lues
    unread_notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    context = {
        'total_clients': total_clients,
        'total_suppliers': total_suppliers,
        'total_users': total_users,
        'stock_value': stock_value,
        'low_stock_count': len(low_stock_products),
        'rupture_count': len(rupture_products),
        'low_stock_products': low_stock_products[:5],
        'rupture_products': rupture_products[:5],
        'pending_transfers': pending_transfers,
        'pending_receipts': pending_receipts,
        'recent_invoices': recent_invoices,
        'recent_deliveries': recent_deliveries,
        'recent_movements': recent_movements,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'dashboard/admin.html', context)


@login_required
def dashboard_manager(request):
    """Dashboard Manager — focus achats et approvisionnements."""
    if not (request.user.is_manager or request.user.is_admin):
        return redirect('dashboard')

    from apps.suppliers.models import Supplier
    from apps.deliveries.models import SupplierInvoice
    from apps.stock.models import StockBalance, Warehouse, StockMovement
    from apps.products.models import Product

    total_suppliers = Supplier.objects.filter(is_active=True).count()
    total_invoices = SupplierInvoice.objects.count()

    # Montant total achats
    from django.db.models import Sum
    total_purchase = SupplierInvoice.objects.filter(
        status='validated'
    ).aggregate(
        total=Sum('lines__total_price_ht')
    )['total'] or 0

    # Factures récentes
    recent_invoices = SupplierInvoice.objects.select_related(
        'supplier', 'created_by'
    ).order_by('-created_at')[:10]

    draft_invoices = SupplierInvoice.objects.filter(status='draft').count()
    validated_invoices = SupplierInvoice.objects.filter(status='validated').count()

    # Stock principal
    main_warehouse = Warehouse.objects.filter(warehouse_type='main').first()
    main_stock_items = []
    if main_warehouse:
        main_stock_items = StockBalance.objects.filter(
            warehouse=main_warehouse,
            quantity__gt=0
        ).select_related('product', 'product__category').order_by(
            'product__designation'
        )[:20]

    # Produits récemment approvisionnés
    recent_entries = StockMovement.objects.filter(
        movement_type='entree_fournisseur'
    ).select_related('product', 'created_by').order_by('-created_at')[:10]

    context = {
        'total_suppliers': total_suppliers,
        'total_invoices': total_invoices,
        'total_purchase': total_purchase,
        'recent_invoices': recent_invoices,
        'draft_invoices': draft_invoices,
        'validated_invoices': validated_invoices,
        'main_stock_items': main_stock_items,
        'recent_entries': recent_entries,
        'main_warehouse': main_warehouse,
    }
    return render(request, 'dashboard/manager.html', context)


@login_required
def dashboard_magasinier(request):
    """Dashboard Magasinier — focus stock principal et transferts."""
    if not (request.user.is_magasinier or request.user.is_admin):
        return redirect('dashboard')

    from apps.stock.models import StockBalance, Warehouse, StockMovement
    from apps.deliveries.models import InternalDelivery

    main_warehouse = Warehouse.objects.filter(warehouse_type='main').first()

    # Stock principal
    low_stock_items = []
    total_products = 0
    if main_warehouse:
        balances = StockBalance.objects.filter(
            warehouse=main_warehouse
        ).select_related('product', 'product__category')
        total_products = balances.filter(quantity__gt=0).count()
        low_stock_items = [
            b for b in balances
            if b.quantity <= b.product.min_stock_level and b.quantity > 0
        ][:10]

    # Transferts
    sent_transfers = InternalDelivery.objects.filter(
        status__in=['valide', 'en_transit', 'recu']
    ).order_by('-created_at')[:5]

    pending_transfers = InternalDelivery.objects.filter(
        status='en_transit'
    ).select_related('technician').count()

    # Mouvements récents
    recent_movements = StockMovement.objects.filter(
        warehouse=main_warehouse
    ).select_related('product', 'created_by').order_by('-created_at')[:10] if main_warehouse else []

    context = {
        'main_warehouse': main_warehouse,
        'total_products': total_products,
        'low_stock_items': low_stock_items,
        'low_stock_count': len(low_stock_items),
        'sent_transfers': sent_transfers,
        'pending_transfers': pending_transfers,
        'recent_movements': recent_movements,
    }
    return render(request, 'dashboard/magasinier.html', context)


@login_required
def dashboard_technicien(request):
    """
    Dashboard Technicien — mobile-first.
    RÈGLE : AUCUN PRIX, AUCUNE VALEUR MONÉTAIRE.
    """
    if not (request.user.is_technicien or request.user.is_admin):
        return redirect('dashboard')

    from apps.stock.models import StockBalance, Warehouse, StockMovement
    from apps.deliveries.models import InternalDelivery, CustomerDelivery

    # Entrepôt du technicien
    tech_warehouse = Warehouse.objects.filter(
        warehouse_type='technicien',
        owner=request.user
    ).first()

    # Stock du technicien (SANS PRIX)
    my_stock = []
    low_stock_items = []
    total_items = 0
    if tech_warehouse:
        balances = StockBalance.objects.filter(
            warehouse=tech_warehouse
        ).select_related('product', 'product__category').order_by('product__designation')
        my_stock = balances.filter(quantity__gt=0)
        total_items = my_stock.count()
        low_stock_items = [b for b in my_stock if b.quantity <= 2][:5]

    # Arrivages en attente (transferts en transit vers ce technicien)
    pending_arrivals = InternalDelivery.objects.filter(
        technician=request.user,
        status='en_transit'
    ).select_related('created_by').order_by('-created_at')

    # BL clients récents (SANS PRIX)
    recent_bl = CustomerDelivery.objects.filter(
        technician=request.user
    ).select_related('client').order_by('-created_at')[:5]

    # Mouvements récents de son stock (SANS PRIX)
    recent_movements = StockMovement.objects.filter(
        warehouse=tech_warehouse
    ).select_related('product').order_by('-created_at')[:10] if tech_warehouse else []

    context = {
        'tech_warehouse': tech_warehouse,
        'my_stock': my_stock[:10],
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'pending_arrivals': pending_arrivals,
        'pending_count': pending_arrivals.count(),
        'recent_bl': recent_bl,
        'recent_movements': recent_movements,
        'show_prices': False,  # JAMAIS
    }
    return render(request, 'dashboard/technicien.html', context)
