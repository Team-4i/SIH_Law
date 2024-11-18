from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/card-room/(?P<room_id>[^/]+)/$', consumers.RoomConsumer.as_asgi()),
    re_path(r'ws/game/(?P<room_id>[^/]+)/$', consumers.GameConsumer.as_asgi()),
]