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
    return render_template("index.html")  # serve the HTML page

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return {"error": "No text provided"}, 400

    audio_bytes = asyncio.run(get_tts_audio(text))

    return Response(
        audio_bytes,
        mimetype="audio/wav"  # browser will treat this as audio
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
