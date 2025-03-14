from django.shortcuts import render
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def mark_notification_as_read(request):
    user = request.user
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}", 
        {
            "type": "send_notification",
            "unread_count": 0,  # Reset unread count
        }
    )

    notify_list = Notification.objects.all().order_by('-created_at').exclude(notification_type="message")
    context = {
        'notify_list' : notify_list,
    }

    return render(request,'notification/noti-list.html', context)
