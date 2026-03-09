"""URLs Produits."""
from django.urls import path
from .views import (
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView,
    CategoryListView, CategoryCreateView, CategoryUpdateView,
)

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('nouveau/', ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/modifier/', ProductUpdateView.as_view(), name='product_update'),

    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/nouveau/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/modifier/', CategoryUpdateView.as_view(), name='category_update'),
]
