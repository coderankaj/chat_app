import json
import uuid

from redis.asyncio import Redis
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


REDIS_URL = "redis://127.0.0.1:6379"

class UserPresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection with proper connection tracking"""
        self.redis = Redis.from_url(REDIS_URL, decode_responses=True)
        self.user = self.scope["user"]
        self.connection_id = str(uuid.uuid4())

        # Accept connection first to enable communication
        await self.accept()

        # Track connection in Redis
        if isinstance(self.user, AnonymousUser):
            await self._track_anonymous_connection()
        else:
            await self._track_authenticated_connection()

        # Add to presence group and send initial status
        await self.channel_layer.group_add("presence_updates", self.channel_name)
        await self._broadcast_presence()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection with atomic Redis operations"""
        pipeline = self.redis.pipeline()

        if isinstance(self.user, AnonymousUser):
            pipeline.srem("anonymous_connections", self.connection_id)
        else:
            pipeline.hincrby("user_connections", self.user.id, -1)
            pipeline.hdel("user_connections", self.user.id)

        await pipeline.execute()
        await self.channel_layer.group_discard("presence_updates", self.channel_name)
        await self._broadcast_presence()

    async def _track_authenticated_connection(self):
        """Track authenticated user connection with connection count"""
        await self.redis.hincrby("user_connections", self.user.id, 1)

    async def _track_anonymous_connection(self):
        """Track anonymous connection with unique ID"""
        await self.redis.sadd("anonymous_connections", self.connection_id)

    async def _get_presence_data(self):
        """Get current presence data from Redis atomically"""
        pipeline = self.redis.pipeline()
        pipeline.hlen("user_connections")
        pipeline.scard("anonymous_connections")
        logged_in, anonymous = await pipeline.execute()

        return {
            "logged_in_users": logged_in,
            "anonymous_users": anonymous,
            "total_connections": logged_in + anonymous
        }

    async def _broadcast_presence(self):
        """Broadcast presence update to all connected clients"""
        presence_data = await self._get_presence_data()
        await self.channel_layer.group_send(
            "presence_updates",
            {
                "type": "presence.update",
                "data": presence_data
            }
        )

    async def presence_update(self, event):
        """Send presence updates to WebSocket client"""
        await self.send(text_data=json.dumps(event["data"]))
