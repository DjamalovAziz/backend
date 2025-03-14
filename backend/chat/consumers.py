# backend\chat\consumers.py:

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Channel, Message
from user.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.channel_uuid = self.scope['url_route']['kwargs']['channel_uuid']
        self.room_group_name = f'chat_{self.channel_uuid}'
        
        # Проверка доступа пользователя к каналу
        if await self.check_user_channel_access():
            # Присоединяемся к группе канала
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        # Покидаем группу канала
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Сохраняем сообщение в БД
        db_message = await self.save_message(message)
        
        # Отправляем сообщение в группу канала
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': str(self.user.uuid),
                'username': self.user.username,
                'message_id': str(db_message.uuid),
                'created_at': db_message.created_at.isoformat()
            }
        )
    
    async def chat_message(self, event):
        # Отправляем сообщение WebSocket клиенту
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'message_id': event['message_id'],
            'created_at': event['created_at']
        }))
    
    @database_sync_to_async
    def check_user_channel_access(self):
        # Проверяем, есть ли у пользователя доступ к каналу
        try:
            channel = Channel.objects.get(uuid=self.channel_uuid)
            return channel.groups.filter(members=self.user).exists()
        except Channel.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        # Сохраняем сообщение в БД
        channel = Channel.objects.get(uuid=self.channel_uuid)
        message = Message.objects.create(
            channel=channel,
            sender=self.user,
            content=content
        )
        return message