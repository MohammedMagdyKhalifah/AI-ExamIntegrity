# integrity_app/consumers.py

import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from deepgram import Deepgram
from dotenv import load_dotenv

load_dotenv()

class TranscriptConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.dg_client = Deepgram(os.getenv('DEEPGRAM_API_KEY'))
        try:
            self.dg_socket = await self.dg_client.transcription.live({'punctuate': True, 'interim_results': False})
            self.dg_socket.registerHandler(self.dg_socket.event.TRANSCRIPT_RECEIVED, self.get_transcript)
        except Exception as e:
            await self.close()
            raise Exception(f'Could not open Deepgram socket: {e}')
        await self.accept()

    async def get_transcript(self, data):
        # Extract transcript text from Deepgram response.
        transcript = data.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
        if transcript:
            await self.send(text_data=json.dumps({'transcript': transcript}))

    async def disconnect(self, close_code):
        if hasattr(self, 'dg_socket'):
            self.dg_socket.close()

    async def receive(self, bytes_data=None, text_data=None):
        if bytes_data:
            self.dg_socket.send(bytes_data)