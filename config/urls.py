"""StockSage — URL Configuration principale."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),

    # Auth
    path('auth/', include('apps.users.urls.auth')),

    # Dashboard
    path('dashboard/', include('apps.users.urls.dashboard')),

    # Modules métier (web)
    path('clients/', include('apps.clients.urls')),
    path('fournisseurs/', include('apps.suppliers.urls')),
    path('produits/', include('apps.products.urls')),
    path('stock/', include('apps.stock.urls')),
    path('livraisons/', include('apps.deliveries.urls')),
    path('inventaire/', include('apps.inventory.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('rapports/', include('apps.reports.urls')),
    path('utilisateurs/', include('apps.users.urls.users')),

    # API REST
    path('api/v1/', include([
        # Auth JWT
        path('auth/', include('apps.users.api.urls')),
        # Modules API
        path('clients/', include('apps.clients.api.urls')),
        path('fournisseurs/', include('apps.suppliers.api.urls')),
        path('produits/', include('apps.products.api.urls')),
        path('stock/', include('apps.stock.api.urls')),
        path('livraisons/', include('apps.deliveries.api.urls')),
        path('inventaire/', include('apps.inventory.api.urls')),
        path('notifications/', include('apps.notifications.api.urls')),
        path('dashboard/', include('apps.users.api.dashboard_urls')),
    ])),

    # Documentation API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redirection racine
    path('', include('apps.users.urls.home')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Config admin
admin.site.site_header = 'StockSage Administration'
admin.site.site_title = 'StockSage'
admin.site.index_title = 'Tableau de bord administrateur'
