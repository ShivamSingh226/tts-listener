from flask import Flask, request, jsonify
import asyncio
import websockets
import os
app = Flask(__name__)

TTS_SERVER_URI = "wss://tts-executer.onrender.com/ws"  # Update this if your TTS server is hosted externally

async def send_text_to_tts(text):
    async with websockets.connect(TTS_SERVER_URI, max_size=None) as websocket:
        await websocket.send(text)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    payload = data.get("payload", {})
    text = payload.get("text", "")
    sender_fullname = payload.get("senderFullname", "")

    if sender_fullname != "tiledesk-tts":
        return jsonify({"status": "ignored", "message": "Sender not authorized"}), 200

    if not text:
        return jsonify({"status": "error", "message": "No text found"}), 400

    asyncio.run(send_text_to_tts(text))
    return jsonify({"status": "success", "message": "Text forwarded to TTS server"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render needs $PORT
    print(f"✅ Flask server is up and running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)