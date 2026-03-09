"""API Views — Dashboard et utilisateur courant."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.clients.models import Client
        from apps.suppliers.models import Supplier
        from apps.stock.models import Warehouse, StockBalance
        from apps.notifications.models import Notification

        main_warehouse = Warehouse.objects.filter(warehouse_type='main').first()
        stock_value = 0
        low_stock_count = 0
        if main_warehouse:
            from apps.stock.services import get_stock_stats
            stats = get_stock_stats(main_warehouse)
            stock_value = float(stats['total_value'])
            low_stock_count = stats['low_stock_count']

        return Response({
            'clients': Client.objects.filter(is_active=True).count(),
            'suppliers': Supplier.objects.filter(is_active=True).count(),
            'stock_value': stock_value if request.user.can_see_prices else None,
            'low_stock_count': low_stock_count,
            'unread_notifications': Notification.objects.filter(
                user=request.user, is_read=False
            ).count(),
        })
