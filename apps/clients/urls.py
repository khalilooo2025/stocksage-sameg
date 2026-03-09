"""URLs Clients."""
from django.urls import path
from .views import ClientListView, ClientDetailView, ClientCreateView, ClientUpdateView, client_toggle_active

urlpatterns = [
    path('', ClientListView.as_view(), name='client_list'),
    path('nouveau/', ClientCreateView.as_view(), name='client_create'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('<int:pk>/modifier/', ClientUpdateView.as_view(), name='client_update'),
    path('<int:pk>/activer/', client_toggle_active, name='client_toggle_active'),
]
