"""URLs gestion des utilisateurs."""
from django.urls import path
from apps.users.views.users import UserListView, UserCreateView, UserUpdateView, user_toggle_active

urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('nouveau/', UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/modifier/', UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/activer/', user_toggle_active, name='user_toggle_active'),
]
