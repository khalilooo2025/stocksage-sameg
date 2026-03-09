"""URLs d'authentification."""
from django.urls import path
from apps.users.views.auth import login_view, logout_view, profile_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
]
