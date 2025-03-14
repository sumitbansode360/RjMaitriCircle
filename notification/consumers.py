import json
from channels.generic.websocket import AsyncWebsocketConsumer
from notification.models import Notification
from asgiref.sync import sync_to_async
from chat.models import GroupMessage
from django.db import models

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""

        self.user = self.scope["user"]
        print(f"📢 WebSocket connection attempt by {self.user}")  # ✅ Debugging
        if self.user.is_authenticated:
            self.room_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            print(f"📢 User {self.user} added to group {self.room_name}")  # ✅ Debugging

        else:
            print("❌ WebSocket connection rejected (User not authenticated)")  # ✅ Debugging
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""

        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        pass

    async def send_notification(self, event):
        """Send real-time notifications to clients."""
        notification = event.get('notification')  # Safely get the 'notification' key
        print(notification, "1st")
        if notification is not None:
            notification['unread_notification'] = await self.get_unread_count()
            print(notification)
            await self.send(text_data=json.dumps(notification))

        else:
            # If 'notification' does not exist, send only the unread count
            unread_notification_count = event.get('unread_count', 0)  # Default to 0 if 'unread_count' is missing
            await self.send(text_data=json.dumps({'unread_notification': unread_notification_count}))
                
    @sync_to_async
    def get_unread_count(self):
        """Fetch unread notifications count asynchronously."""
        return Notification.objects.filter(user=self.user, is_read=False).count()
    
    # chat message notificttions 
    async def send_message_notification(self, event):
        """Send real-time notifications to clients with per-user unread message counts."""
        notification = event.get('message_notification')

        if notification is not None:
            print("📢 Sending message notification")
            
            # 🔥 Fetch unread messages count per sender
            unread_counts = await self.get_message_unread_count_per_sender()
            total_unread_count  = await self.get_total_unread_count()
            
            notification['unread_message_counts'] = unread_counts  # Attach per-sender counts
            notification['total_unread_count'] = total_unread_count   # Attach per-sender counts
            print(notification)
            
            await self.send(text_data=json.dumps(notification))
        else:
            print("📢 Resetting unread message count")
            
            # 🔥 Only send unread message counts
            unread_counts = await self.get_message_unread_count_per_sender()
            await self.send(text_data=json.dumps({'unread_message_counts': unread_counts}))


    # for chat messages
    @sync_to_async
    def get_message_unread_count_per_sender(self):
        """Returns a dictionary {sender_id: unread_count}."""
        unread_messages = (
            Notification.objects.filter(user=self.user, is_read=False, notification_type="message")
            .values('sender')
            .annotate(unread_count=models.Count('id'))
        )
        print("Unread messages:", list(unread_messages))

        return {msg['sender']: msg['unread_count'] for msg in unread_messages}
    
    @sync_to_async
    def get_total_unread_count(self):
        """Returns the total unread messages count for the user."""
        return Notification.objects.filter(user=self.user, is_read=False, notification_type="message").count()
