# backend\chat\consumers.py:

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PersonalChat, GroupChat, Message
from user.models import User


class BaseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": str(self.user.uuid),
                "sender_username": self.user.username,
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "sender_username": event["sender_username"],
                }
            )
        )


class PersonalChatConsumer(BaseChatConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        self.room_group_name = f"personal_chat_{self.chat_uuid}"

        # Проверка, есть ли пользователь в участниках чата
        if not await self.is_chat_participant():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    @database_sync_to_async
    def is_chat_participant(self):
        try:
            chat = PersonalChat.objects.get(uuid=self.chat_uuid)
            return chat.participants.filter(uuid=self.user.uuid).exists()
        except PersonalChat.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        chat = PersonalChat.objects.get(uuid=self.chat_uuid)
        return Message.objects.create(
            sender=self.user, content=content, personal_chat=chat
        )


from django.contrib.auth import get_user_model
from django.conf import settings
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class GroupChatConsumer(BaseChatConsumer):
    async def connect(self):
        print("WebSocket connect handler called")

        # Extract token from headers and authenticate directly
        headers = dict(self.scope["headers"])
        authenticated = False

        if b"authorization" in headers:
            print("Found Authorization header")
            try:
                auth_header = headers[b"authorization"].decode()
                print(f"Auth header: {auth_header[:20]}...")

                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    print(f"Extracted token: {token[:20]}...")

                    try:
                        # Decode token without verification first to see content
                        import base64
                        import json

                        token_parts = token.split(".")
                        if len(token_parts) == 3:
                            payload_part = token_parts[1]
                            # Add padding
                            payload_part += "=" * ((4 - len(payload_part) % 4) % 4)
                            payload_bytes = base64.urlsafe_b64decode(payload_part)
                            payload = json.loads(payload_bytes)
                            print(f"Raw token payload: {payload}")

                            # Get user_id from payload
                            user_id = payload.get("user_id")
                            print(f"User ID from payload: {user_id}")

                            # Try to get user
                            if user_id:
                                self.user = await self.get_user_by_uuid(user_id)
                                print(
                                    f"Got user: {self.user}, Anonymous: {self.user.is_anonymous}"
                                )
                                authenticated = not self.user.is_anonymous
                            else:
                                print("No user_id in token payload")
                                self.user = AnonymousUser()
                        else:
                            print(f"Invalid token format")
                            self.user = AnonymousUser()
                    except Exception as e:
                        print(f"Error inspecting token payload: {str(e)}")
                        self.user = AnonymousUser()
                else:
                    print(f"Auth header doesn't start with 'Bearer '")
                    self.user = AnonymousUser()
            except Exception as e:
                print(f"Error processing auth header: {str(e)}")
                self.user = AnonymousUser()
        else:
            print("No Authorization header found")
            self.user = AnonymousUser()

        # Check authentication result
        if not authenticated:
            print("Authentication failed, closing connection")
            await self.close(code=4003)
            return

        # Extract chat UUID from URL
        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        print(f"Connecting to chat with UUID: {self.chat_uuid}")

        self.room_group_name = f"group_chat_{self.chat_uuid}"

        # Check if user is participant
        print("Checking if user is a chat participant")
        is_participant = await self.is_chat_participant()
        print(f"Is participant check result: {is_participant}")

        if not is_participant:
            print(f"User {self.user} is not a participant in chat {self.chat_uuid}")
            await self.close(code=4004)
            return

        # Add to channel group
        print(f"Adding channel to group: {self.room_group_name}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the connection
        print("Accepting WebSocket connection")
        await self.accept()
        print(
            f"WebSocket connected successfully for user {self.user} in chat {self.chat_uuid}"
        )

    async def disconnect(self, close_code):
        print(f"WebSocket disconnect with code: {close_code}")

        if hasattr(self, "room_group_name"):
            print(f"Removing from group: {self.room_group_name}")
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    @database_sync_to_async
    def get_user_by_uuid(self, user_uuid):
        try:
            print(f"Looking up user with UUID: {user_uuid}")
            return User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            print(f"User with UUID {user_uuid} not found in database")
            return AnonymousUser()
        except Exception as e:
            print(f"Error looking up user: {str(e)}")
            return AnonymousUser()

    @database_sync_to_async
    def is_chat_participant(self):
        from chat.models import GroupChat  # Import here to avoid circular imports

        try:
            print(f"Looking up chat with UUID: {self.chat_uuid}")
            chat = GroupChat.objects.get(uuid=self.chat_uuid)

            print(
                f"Checking if user {self.user.uuid} is participant in chat {self.chat_uuid}"
            )
            result = chat.participants.filter(uuid=self.user.uuid).exists()

            print(f"Participant check result: {result}")
            return result
        except GroupChat.DoesNotExist:
            print(f"Chat with UUID {self.chat_uuid} does not exist")
            return False
        except Exception as e:
            print(f"Error checking chat participation: {str(e)}")
            return False

    @database_sync_to_async
    def save_message(self, content):
        chat = GroupChat.objects.get(uuid=self.chat_uuid)
        return Message.objects.create(
            sender=self.user, content=content, group_chat=chat
        )
