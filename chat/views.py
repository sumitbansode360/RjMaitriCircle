from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from chat.models import ChatGroup
from .forms import *
from userauths.models import User
from django.http import Http404, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notification.models import Notification
from django.db.models import Count


@login_required
def chat_view(request, chatroom_name='public'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatMessageCreateForm()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.group = chat_group
            print(f"{request.user} sending a new message to {other_user}")

            message.save()
            
            print(f"{request.user} sending a new message to {other_user}")

            context = {
                'message': message,
                'user': request.user,
            }

            return render(request, 'chat/partials/chat_message_p.html', context)


    # Reset unread_count for the other user when the chat is viewed
    
    if other_user:
        # Mark all unread messages as read for the current user in this chat group
        Notification.objects.filter(user=request.user, is_read=False, sender=other_user, notification_type="message").update(is_read=True)



        # Send a WebSocket message to the other user's personal group to reset their unread_count
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{request.user.id}",
            {
                "type": "send_message_notification",
                "message_notification": {
                    "group" : {
                        "name": chatroom_name,  
                    },
                
            
                "notification_message": "",
                "unread_message_notification": 0,  # Reset unread count
                }
            }
        )

    unread_counts = (
        Notification.objects.filter(user=request.user, is_read=False, notification_type="message")
        .values('sender')
        .annotate(unread_count=Count('id'))
    )

    unread_message_counts = {msg['sender']: msg['unread_count'] for msg in unread_counts}

    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group,
        "unread_message_counts": unread_message_counts  

    }

    return render(request, 'chat/chat.html', context)


def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')
    
    other_user = User.objects.get(username = username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)

    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
            else:
                chatroom = ChatGroup.objects.create(is_private =True)
                chatroom.members.add(other_user, request.user)
    else:
        chatroom = ChatGroup.objects.create(is_private =True)
        chatroom.members.add(other_user, request.user) 
        
    return redirect('chatroom', chatroom.group_name)

def chat_file_upload(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file = file,
            user = request.user,
            group = chat_group,
        )
        channel_layer = get_channel_layer()
        event = {
            'type' : 'messsage_handler',
            'message_id' : message.id,
        }
        async_to_sync(channel_layer.group_send)(
            chatroom_name, event
        )
    return HttpResponse()