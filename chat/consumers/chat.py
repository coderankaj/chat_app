import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now

from chat.models import Channel, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection for chat messages."""
        if self.scope["scheme"] != "wss":
            await self.close(code=4003)
            return

        self.user = self.scope["user"]
        self.channel_id = self.scope["url_route"]["kwargs"].get("channel_id")
        self.room_group_name = f"chat_{self.channel_id}"

        # Accept connection first to allow sending messages
        await self.accept()

        if not self.user.is_authenticated:
            await self.send_error("Authentication required. Connection closed.", close_connection=True)
            return

        if not self.channel_id:
            await self.send_error("No channel_id supplied. Connection closed.", close_connection=True)
            return

        if not await self.channel_exists():
            await self.send_error("Invalid channel ID. Connection closed.", close_connection=True)
            return

        # Join the chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Send join notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": f"{self.user.username} has joined the chat.",
                "username": "System",
                "channel_id": self.channel_id,
                "timestamp": str(now()),
            },
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name') and self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": f"{self.user.username} has left the chat.",
                    "username": "System",
                    "channel_id": self.channel_id,
                    "timestamp": str(now()),
                },
            )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming chat messages."""
        if not self.user.is_authenticated:
            await self.send_error("Authentication required. Connection closed.", close_connection=True)
            return

        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()

            if not message:
                await self.send_error("Message content cannot be empty.")
                return

            # Save message to database
            message_obj = await self.save_message(message)

            # Broadcast message to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.user.username,
                    "channel_id": self.channel_id,
                    "timestamp": str(message_obj.timestamp),
                },
            )

        except json.JSONDecodeError:
            await self.send_error("Invalid message format.")
        except Exception:
            await self.send_error("An error occurred while processing your message.")

    async def chat_message(self, event):
        """Send chat messages to WebSocket clients."""
        await self.send(text_data=json.dumps(event))

    async def send_error(self, message, close_connection=False):
        """Send an error message to the client."""
        await self.send(text_data=json.dumps({
            "message": message
        }))
        if close_connection:
            await self.close()

    async def channel_exists(self):
        """Check if channel exists."""
        return await Channel.objects.filter(id=self.channel_id).aexists()

    async def save_message(self, message_content):
        """Save message to database."""
        channel = await Channel.objects.aget(id=self.channel_id)
        return await Message.objects.acreate(
            channel=channel,
            sender=self.user,
            content=message_content
        )
