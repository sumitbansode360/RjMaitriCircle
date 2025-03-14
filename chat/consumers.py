from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import json
from .models import *
from asgiref.sync import async_to_sync
from notification.models import Notification
from channels.layers import get_channel_layer

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        # Get the chatroom name from the URL
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        async_to_sync (self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        # add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()


        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )
        # remove user count
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']


        message = GroupMessage.objects.create(
            body=body,
            user = self.user,
            group = self.chatroom
        )

        event = {
            'type': 'message_handler',
            'message_id': message.id
        }
        print(f"📢 Sending message notification to group {self.chatroom_name}")
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

        
        channel_layer = get_channel_layer()

        # Notify all users in the chatroom except the sender
        for user in self.chatroom.members.all():
            if user != self.user:  # ✅ Send only to other members
                # send notification to user with count of unread message
                notification = Notification.objects.create(
                    user = user,
                    sender = self.user,
                    notification_type = "message",
                    message = f"new message from {message.user} to the {self.chatroom}"
                )
                print(f"📢 Sending WebSocket notification to user_{user.id}")  # ✅ Debugging
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}",  # ✅ Send to the receiver
                    {
                        "type": "send_message_notification",
                        "message_notification": { 
                            "group": {
                                "name": self.chatroom.group_name,  
                                "sender_id" : self.user.id
                            },
                            "id": notification.id,
                            "image": notification.sender.profile.image.url if notification.sender.profile and notification.sender.profile.image else "/static/default-profile.png",
                            "notification_type": notification.notification_type,
                            "message": notification.message,
                            "timestamp": str(notification.created_at),
                        }
                    }
                )


    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user' : self.user,
        }
        html = render_to_string('chat/partials/chat_message_p.html', context=context)
        self.send(text_data = html)

    def update_online_count(self):
        online_count = self.chatroom.users_online.count() -1
        event = {
            'type' : 'online_count_handler',
            'online_count' : online_count
        }
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)


    def online_count_handler(self, event):
        online_count = event['online_count']
        html = render_to_string('chat/partials/online_count.html', {'online_count' : online_count})
        self.send(text_data=html)