from flask import Flask, request, Response, render_template
import asyncio
import websockets

app = Flask(__name__)

TTS_SERVER_URI = "wss://tts-executer.onrender.com/ws"

async def get_tts_audio(text: str):
    async with websockets.connect(TTS_SERVER_URI, max_size=None) as websocket:
        await websocket.send(text)
        audio_bytes = await websocket.recv()
        return audio_bytes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/play")
def play():
    return render_template("play.html")

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json(force=True)

    text = None

    # Case 1: simple payload { "text": "..." }
    if "text" in data:
        text = data.get("text")

    # Case 2: Tiledesk payload { "payload": { "senderFullname": "...", "text": "..." } }
    elif "payload" in data:
        payload = data.get("payload", {})
        if payload.get("senderFullname") == "tiledesk-tts":
            text = payload.get("text")

    if not text:
        return {"error": "No valid TTS text provided"}, 400

    audio_bytes = asyncio.run(get_tts_audio(text))

    return Response(
        audio_bytes,
        mimetype="audio/wav"
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
