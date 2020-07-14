from .models import Notification


def unread_notifications_count(request):
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(
            is_viewed=False,
            user=request.user,
        ).count()
    return {'unread_notifications_count': unread_notifications_count}
