from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category-api')
router.register('', ProductViewSet, basename='product-api')
urlpatterns = router.urls
