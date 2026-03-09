"""URLs Rapports."""
from django.urls import path
from .views import reports_dashboard, report_stock
from .export_views import (
    export_products_view, export_clients_view, export_suppliers_view,
    export_stock_view, export_deliveries_view, export_invoices_view,
    export_stock_movements_view, import_export_admin
)

urlpatterns = [
    path('', reports_dashboard, name='reports_dashboard'),
    path('stock/', report_stock, name='report_stock'),

    # Export endpoints
    path('export/produits/', export_products_view, name='export_products'),
    path('export/clients/', export_clients_view, name='export_clients'),
    path('export/fournisseurs/', export_suppliers_view, name='export_suppliers'),
    path('export/stock/', export_stock_view, name='export_stock'),
    path('export/livraisons/', export_deliveries_view, name='export_deliveries'),
    path('export/factures/', export_invoices_view, name='export_invoices'),
    path('export/historique-stock/', export_stock_movements_view, name='export_stock_movements'),

    # Import/Export admin page
    path('import-export/', import_export_admin, name='import_export_admin'),
]
