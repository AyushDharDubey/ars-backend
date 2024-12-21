import json
from .models import Message, Team
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class TeamChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.team_id = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"team_{self.team_id}"

        # Verify if the team exists
        try:
            self.team = await sync_to_async(Team.objects.get)(id=self.team_id)
        except Team.DoesNotExist:
            await self.close()
            return

        # Join room group
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
        message_content = data.get("content")
        user = self.scope["user"]

        # Save message to the database
        message = await sync_to_async(Message.objects.create)(
            user=user,
            team=self.team,
            content=message_content,
        )

        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "content": message.content,
                "username": user.username,
                "timestamp": message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "content": event["content"],
            "username": event["username"],
            "timestamp": event["timestamp"],
        }))
