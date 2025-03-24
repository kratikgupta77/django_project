import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message, UserKeys
import base64
import rsa

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f"chat_{self.room_name}"

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
        data = json.loads(text_data)
        sender = self.scope["user"]
        receiver_username = data["receiver"]
        message_text = data["message"]

        receiver = User.objects.get(username=receiver_username)

        # Encrypt message
        receiver_keys = UserKeys.objects.get(user=receiver)
        public_key = rsa.PublicKey.load_pkcs1(receiver_keys.public_key.encode())
        encrypted_message = base64.b64encode(rsa.encrypt(message_text.encode(), public_key)).decode()

        # Store message in DB
        message = Message(sender=sender, receiver=receiver, encrypted_text=encrypted_message)
        message.save()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender": sender.username,
                "message": encrypted_message,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
