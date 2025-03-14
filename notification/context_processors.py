from notification.models import Notification  # Adjust model import

def unread_message_count(request):
    if request.user.is_authenticated:
        return {
            "unread_message_count": Notification.objects.filter(user=request.user, is_read=False, notification_type="message").count()
        }
    return {"unread_message_count": 0}

def unread_count(request):
    if request.user.is_authenticated:
        return {
            "unread_count": Notification.objects.filter(user=request.user, is_read=False).exclude(notification_type="message").count()
        }
    return {"unread_count": 0}
