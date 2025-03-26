from django.urls import re_path

from chat.consumers import ChatConsumer, UserPresenceConsumer

websocket_urlpatterns = [
    # WebSocket URL for channel chat, where channel_id is passed as a URL parameter.
    re_path(r'ws/chat/(?P<channel_id>[\w-]+)/$', ChatConsumer.as_asgi()),
    re_path(r"ws/user_presence/$", UserPresenceConsumer.as_asgi()),
]
