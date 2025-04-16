import asyncio
import websockets
import json
import base64
import wave


async def test_websocket():
    # 1. Generate test audio file (1 second of silence at 16kHz)
    with wave.open('test.wav', 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)  # 16-bit
        f.setframerate(16000)
        f.writeframes(b'\x00' * 16000 * 2)  # 1 second of silence

    # 2. Read and encode the audio
    with open('test.wav', 'rb') as audio_file:
        audio_bytes = audio_file.read()
        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')

    # 3. Connect and test
    try:
        async with websockets.connect('ws://localhost:8000/ws/process_audio/') as ws:
            print("✅ WebSocket connected")

            # Send valid message format
            message = json.dumps({
                "audio_data": b64_audio,
                "sample_rate": 16000
            })
            await ws.send(message)
            print("📤 Sent test audio")

            # Get response
            response = await ws.recv()
            print("📥 Received:", json.loads(response))

    except Exception as e:
        print("❌ Connection failed:", str(e))


if __name__ == "__main__":
    asyncio.run(test_websocket())