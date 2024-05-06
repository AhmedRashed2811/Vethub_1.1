from django.urls import path
from Application.consumers import ChatConsumer
from Application.consumers import ChatsConsumer

websocket_urlpatterns = [
    path('ws/notification/<int:chat_id>', ChatConsumer.as_asgi()),
    path('ws/chats/<int:user_id>', ChatsConsumer.as_asgi()),
]