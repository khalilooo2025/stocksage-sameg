from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, StockBalanceViewSet, StockMovementViewSet

router = DefaultRouter()
router.register('entrepots', WarehouseViewSet, basename='warehouse-api')
router.register('soldes', StockBalanceViewSet, basename='balance-api')
router.register('mouvements', StockMovementViewSet, basename='movement-api')
urlpatterns = router.urls
