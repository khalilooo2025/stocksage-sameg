"""URLs Notifications."""
from django.urls import path
from .views import notification_list, notification_mark_read, notification_mark_all_read

urlpatterns = [
    path('', notification_list, name='notification_list'),
    path('<int:pk>/lire/', notification_mark_read, name='notification_mark_read'),
    path('tout-lire/', notification_mark_all_read, name='notification_mark_all_read'),
]
