import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.user = self.scope['user']
        self.room_group_name = f'chat_{min(self.user.id, int(self.receiver_id))}_{max(self.user.id, int(self.receiver_id))}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.user.id
        receiver_id = int(self.receiver_id)

        # Save message to database
        await sync_to_async(Message.objects.create)(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=message
        )

        # Get the last message's timestamp asynchronously
        last_message = await sync_to_async(lambda: Message.objects.last())()
        timestamp = last_message.timestamp.isoformat() if last_message else None

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'timestamp': timestamp,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))
