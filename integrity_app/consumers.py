import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info("WebSocket connected.")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with close code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        logger.info("Received WebSocket message: %s", text_data)
        try:
            data = json.loads(text_data)
            # Dummy audio processing logic:
            recognized_text = "Processed audio"
            response = {
                'recognized_text': recognized_text,
                'violation_found': False
            }
            await self.send(text_data=json.dumps(response))
            logger.info("Sent response: %s", response)
        except Exception as e:
            logger.error("Error processing message: %s", e)
            await self.send(text_data=json.dumps({'error': 'Processing error'}))