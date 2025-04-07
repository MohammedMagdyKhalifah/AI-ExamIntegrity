import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .monitoring import FaceMonitor, SoundMonitor

# Global instances for WebSocket processing
face_monitor_ws = FaceMonitor()
sound_monitor_ws = SoundMonitor()

class ProctorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        await self.accept()
        # Optionally add the connection to a group keyed by session_id

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Assume binary data is a JPEG image for face monitoring.
            # Process frame synchronously via sync_to_async.
            result = await sync_to_async(face_monitor_ws.process_frame)(bytes_data)
            # Send result as JSON (status and suspicious flag)
            await self.send(text_data=json.dumps({
                "type": "frame_result",
                "status": result["status"],
                "is_suspicious": result["is_suspicious"]
            }))
        elif text_data:
            try:
                data = json.loads(text_data)
                if data.get("type") == "audio_data":
                    # The data field contains base64-encoded audio.
                    audio_base64 = data.get("data")
                    audio_bytes = base64.b64decode(audio_base64)
                    result = await sync_to_async(sound_monitor_ws.process_audio_chunk)(audio_bytes)
                    await self.send(text_data=json.dumps({
                        "type": "audio_result",
                        "results": result
                    }))
                elif data.get("type") == "heartbeat":
                    # Optionally respond to heartbeat messages
                    await self.send(text_data=json.dumps({"type": "heartbeat", "status": "alive"}))
            except Exception as e:
                await self.send(text_data=json.dumps({"error": str(e)}))