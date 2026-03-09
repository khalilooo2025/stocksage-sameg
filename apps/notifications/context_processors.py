"""Context processor — injecte les notifications non lues dans chaque template."""


def notifications(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0, 'recent_notifications': []}
    try:
        from .models import Notification
        unread = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'unread_notifications_count': unread.count(),
            'recent_notifications': unread[:5],
        }
    except Exception:
        return {'unread_notifications_count': 0, 'recent_notifications': []}
