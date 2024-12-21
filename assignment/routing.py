from django.urls import path
from .consumers import TeamChatConsumer

websocket_urlpatterns = [
    path('ws/team/<int:pk>/', TeamChatConsumer.as_asgi()),
]
