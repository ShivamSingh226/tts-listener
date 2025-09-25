from flask import Flask, request, jsonify
import asyncio
import websockets

app = Flask(__name__)

TTS_SERVER_URI = "ws://tts-executer.onrender.com/wss"  # Update this if your TTS server is hosted externally

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
    app.run(port=5000)
    print("✅ Flask server is up and running on http://localhost:5000")
    app.run(host="0.0.0.0",port=5000)