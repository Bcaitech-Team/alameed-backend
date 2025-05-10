import json
import traceback

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from src.apps.support.api.serializers import ChatMessageSerializer
from src.apps.support.models import ChatMessage


@sync_to_async
def get_last_message(room_id):
    try:
        last_message = ChatMessage.objects.filter(room_id=room_id).order_by("-date")[1]
        return ChatMessageSerializer(last_message).data
    except Exception:
        pass


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = "chat_%s" % self.room_id

        # Join room
        if self.user.is_authenticated:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from web socket
    async def receive(self, text_data, **kwargs):
        data = json.loads(text_data)
        message = data.get("message")
        files = data.get("files", [])
        type = data.get("type", "chat_message")

        if type == "chat_message":
            message_data = await self.save_message(
                self.user,
                self.room_id,
                message,
                files,
            )
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": type,
                    "message": message_data,
                    "files": files,
                },
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event.get("message")
        event.get("files", [])
        type = event.get("type")

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": type,
                    "message": message,
                    "files": message.get("file_name"),
                }
            )
        )

    @sync_to_async
    def save_message(
            self,
            user,
            room_id,
            message,
            files,
    ):
        message = ChatMessage.objects.create(
            user=user,
            room_id=room_id,
            message=message,
        )
        if files:
            try:
                message.files.set(files)
            except Exception:
                print(traceback.format_exc())

        return ChatMessageSerializer(message).data
