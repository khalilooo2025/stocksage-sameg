"""API URLs — Dashboard stats."""
from django.urls import path
from .views import DashboardStatsView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='api_dashboard_stats'),
]
