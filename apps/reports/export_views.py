"""Vues d'exportation pour l'admin."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from apps.common.export_utils import (
    export_products_export,
    export_clients_export,
    export_suppliers_export,
    export_stock_export,
    export_deliveries_export,
    export_invoices_export,
    export_stock_movement_history_export,
    import_csv_products,
    import_csv_clients,
    import_csv_suppliers,
)
from apps.products.models import Product
from apps.clients.models import Client
from apps.suppliers.models import Supplier
from apps.stock.models import StockBalance, StockMovement
from apps.deliveries.models import CustomerDelivery, SupplierInvoice


def admin_only(view_func):
    """Decorateur pour restreindre aux admins."""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser and request.user.role != 'admin':
            messages.error(request, "Acces reserve aux administrateurs.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return wrapper


def _requested_export_format(request):
    fmt = request.GET.get('format', 'csv').lower().strip()
    return fmt if fmt in {'csv', 'pdf'} else 'csv'


@login_required
@admin_only
def export_products_view(request):
    """Exporte les produits en CSV ou PDF."""
    products = Product.objects.select_related('category').all()
    return export_products_export(products, file_format=_requested_export_format(request))


@login_required
@admin_only
def export_clients_view(request):
    """Exporte les clients en CSV ou PDF."""
    clients = Client.objects.all()
    return export_clients_export(clients, file_format=_requested_export_format(request))


@login_required
@admin_only
def export_suppliers_view(request):
    """Exporte les fournisseurs en CSV ou PDF."""
    suppliers = Supplier.objects.all()
    return export_suppliers_export(suppliers, file_format=_requested_export_format(request))


@login_required
@admin_only
def export_stock_view(request):
    """Exporte le stock en CSV ou PDF."""
    stock = StockBalance.objects.select_related('warehouse', 'product').all()
    return export_stock_export(stock, file_format=_requested_export_format(request))


@login_required
@admin_only
def export_deliveries_view(request):
    """Exporte les BL clients en CSV ou PDF."""
    deliveries = CustomerDelivery.objects.select_related('client', 'technician').all()
    return export_deliveries_export(deliveries, file_format=_requested_export_format(request))


@login_required
@admin_only
def export_invoices_view(request):
    """Exporte les factures fournisseur en CSV ou PDF."""
    invoices = SupplierInvoice.objects.select_related('supplier').all()
    return export_invoices_export(invoices, file_format=_requested_export_format(request))


@login_required
@admin_only
def export_stock_movements_view(request):
    """Exporte l'historique des mouvements de stock en CSV ou PDF."""
    movements = StockMovement.objects.select_related('warehouse', 'product', 'created_by').all()
    return export_stock_movement_history_export(movements, file_format=_requested_export_format(request))


@login_required
@admin_only
def import_export_admin(request):
    """Page d'accueil pour import/export (pour l'admin)."""
    if request.method == 'POST':
        action = request.POST.get('action')
        file_obj = request.FILES.get('file')

        if not file_obj:
            messages.error(request, "Veuillez selectionner un fichier.")
            return redirect('import_export_admin')

        if not file_obj.name.lower().endswith('.csv'):
            messages.error(request, "Format invalide: seul le format CSV est autorise pour l'import.")
            return redirect('import_export_admin')

        try:
            if action == 'import_products':
                imported, errors = import_csv_products(file_obj)
                if errors:
                    messages.warning(request, f"Importation: {imported} produits importes, {len(errors)} erreurs")
                    for error in errors[:5]:
                        messages.info(request, error)
                else:
                    messages.success(request, f"{imported} produits importes avec succes.")

            elif action == 'import_clients':
                imported, errors = import_csv_clients(file_obj)
                if errors:
                    messages.warning(request, f"Importation: {imported} clients importes, {len(errors)} erreurs")
                    for error in errors[:5]:
                        messages.info(request, error)
                else:
                    messages.success(request, f"{imported} clients importes avec succes.")

            elif action == 'import_suppliers':
                imported, errors = import_csv_suppliers(file_obj)
                if errors:
                    messages.warning(request, f"Importation: {imported} fournisseurs importes, {len(errors)} erreurs")
                    for error in errors[:5]:
                        messages.info(request, error)
                else:
                    messages.success(request, f"{imported} fournisseurs importes avec succes.")
            else:
                messages.error(request, "Action d'import inconnue.")

        except Exception as exc:
            messages.error(request, f"Erreur lors de l'importation: {exc}")

        return redirect('import_export_admin')

    return render(request, 'reports/import_export_admin.html', {
        'title': 'Import/Export de donnees',
    })
