"""URLs Livraisons."""
from django.urls import path
from .views import (
    SupplierInvoiceListView, SupplierInvoiceDetailView, invoice_create, invoice_validate,
    invoice_print,
    InternalDeliveryListView, InternalDeliveryDetailView,
    internal_delivery_create, internal_delivery_send, internal_delivery_receive,
    internal_delivery_print,
    CustomerDeliveryListView, CustomerDeliveryDetailView,
    customer_delivery_create, customer_delivery_edit, customer_delivery_validate,
    customer_delivery_print,
)

urlpatterns = [
    # Factures fournisseur
    path('factures/', SupplierInvoiceListView.as_view(), name='invoice_list'),
    path('factures/nouveau/', invoice_create, name='invoice_create'),
    path('factures/<int:pk>/', SupplierInvoiceDetailView.as_view(), name='invoice_detail'),
    path('factures/<int:pk>/valider/', invoice_validate, name='invoice_validate'),
    path('factures/<int:pk>/imprimer/', invoice_print, name='invoice_print'),

    # BL Internes
    path('bl-internes/', InternalDeliveryListView.as_view(), name='internal_delivery_list'),
    path('bl-internes/nouveau/', internal_delivery_create, name='internal_delivery_create'),
    path('bl-internes/<int:pk>/', InternalDeliveryDetailView.as_view(), name='internal_delivery_detail'),
    path('bl-internes/<int:pk>/envoyer/', internal_delivery_send, name='internal_delivery_send'),
    path('bl-internes/<int:pk>/recevoir/', internal_delivery_receive, name='internal_delivery_receive'),
    path('bl-internes/<int:pk>/imprimer/', internal_delivery_print, name='internal_delivery_print'),

    # BL Clients
    path('bl-clients/', CustomerDeliveryListView.as_view(), name='customer_delivery_list'),
    path('bl-clients/nouveau/', customer_delivery_create, name='customer_delivery_create'),
    path('bl-clients/<int:pk>/', CustomerDeliveryDetailView.as_view(), name='customer_delivery_detail'),
    path('bl-clients/<int:pk>/modifier/', customer_delivery_edit, name='customer_delivery_edit'),
    path('bl-clients/<int:pk>/valider/', customer_delivery_validate, name='customer_delivery_validate'),
    path('bl-clients/<int:pk>/imprimer/', customer_delivery_print, name='customer_delivery_print'),
]
