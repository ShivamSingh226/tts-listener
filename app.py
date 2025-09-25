from flask import Flask, request, jsonify
import asyncio
import websockets
import io
import sounddevice as sd
import soundfile as sf

app = Flask(__name__)
TTS_SERVER_URI = "wss://tts-executer.onrender.com/ws"

async def send_text_and_play_audio(text):
    async with websockets.connect(TTS_SERVER_URI) as websocket:
        await websocket.send(text)
        audio_bytes = await websocket.recv()

        audio_file = io.BytesIO(audio_bytes)
        data, samplerate = sf.read(audio_file, dtype='float32')
        sd.play(data, samplerate)
        sd.wait()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    payload = data.get("payload", {})
    text = payload.get("text", "")
    sender = payload.get("senderFullname", "")

    print(f"📩 Received from {sender}: {text}")

    if sender != "tiledesk-tts":
        return jsonify({"status": "ignored"}), 200

    if not text:
        return jsonify({"status": "error", "message": "No text"}), 400

    asyncio.run(send_text_and_play_audio(text))
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run( port=5000)
