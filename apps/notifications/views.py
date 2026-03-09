"""Vues Notifications."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/list.html', {
        'notifications': notifications[:50],
        'unread_count': unread_count,
    })


@login_required
def notification_mark_read(request, pk):
    Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
    next_url = request.GET.get('next', 'notification_list')
    return redirect(next_url)


@login_required
def notification_mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notification_list')
