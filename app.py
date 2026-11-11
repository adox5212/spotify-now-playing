import asyncio
import json
import subprocess
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

try:
    from winsdk.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager,
        GlobalSystemMediaTransportControlsSessionPlaybackStatus,
    )
    from winsdk.windows.storage.streams import DataReader
    WINSDK_AVAILABLE = True
except Exception as exc:
    WINSDK_AVAILABLE = False
    WINSDK_IMPORT_ERROR = str(exc)

ROOT = Path(__file__).resolve().parent
ART_PATH = ROOT / "static" / "album-art.jpg"

app = Flask(__name__, static_folder="static", template_folder="templates")

state_lock = threading.Lock()
state = {
    "available": False,
    "playing": False,
    "title": "Nothing playing",
    "artist": "Play something on Spotify",
    "album": "",
    "position": 0,
    "duration": 0,
    "art_url": "/static/placeholder.svg",
    "message": "Waiting for Windows media session…",
    "updated": time.time(),
}
last_art_key = None


def seconds(value):
    try:
        return max(0, value.total_seconds())
    except Exception:
        try:
            return max(0, value.duration / 10_000_000)
        except Exception:
            return 0


async def save_thumbnail(thumbnail):
    """Save the current Windows media-session thumbnail, if one is available."""
    if thumbnail is None:
        return False
    try:
        stream = await thumbnail.open_read_async()
        reader = DataReader(stream.get_input_stream_at(0))
        await reader.load_async(stream.size)
        data = bytearray(stream.size)
        reader.read_bytes(data)
        reader.close()
        stream.close()
        if data:
            ART_PATH.write_bytes(data)
            return True
    except Exception:
        return False
    return False


async def read_session():
    global last_art_key
    if not WINSDK_AVAILABLE:
        with state_lock:
            state["message"] = (
                "Windows media integration could not load. "
                "Run install.bat and check the troubleshooting guide."
            )
            state["updated"] = time.time()
        return

    try:
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        session = manager.get_current_session()

        if session is None:
            with state_lock:
                state.update({
                    "available": False,
                    "playing": False,
                    "title": "Nothing playing",
                    "artist": "Start Spotify on this PC",
                    "album": "",
                    "position": 0,
                    "duration": 0,
                    "message": "No active Windows media session detected.",
                    "updated": time.time(),
                })
            return

        props = await session.try_get_media_properties_async()
        playback = session.get_playback_info()
        timeline = session.get_timeline_properties()

        title = props.title or "Unknown title"
        artist = props.artist or "Unknown artist"
        album = props.album_title or ""
        status = playback.playback_status
        playing = status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING

        position = seconds(timeline.position)
        duration = seconds(timeline.end_time) - seconds(timeline.start_time)
        if duration < 0:
            duration = 0

        art_key = (title, artist, album)
        if art_key != last_art_key:
            saved = await save_thumbnail(props.thumbnail)
            if saved:
                last_art_key = art_key

        with state_lock:
            state.update({
                "available": True,
                "playing": playing,
                "title": title,
                "artist": artist,
                "album": album,
                "position": position,
                "duration": duration,
                "art_url": "./static/album-art.jpg?v=" + str(int(time.time())) if ART_PATH.exists() else "./static/placeholder.svg",
                "message": "Playing" if playing else "Spotify is paused",
                "updated": time.time(),
            })
    except Exception as exc:
        with state_lock:
            state["message"] = "Could not read media session: " + str(exc)
            state["updated"] = time.time()


LAST_PUSH_KEY = None


def _push_now_playing():
    try:
        subprocess.run(["git", "add", "docs/now-playing.json"], cwd=str(ROOT), check=False)
        subprocess.run(["git", "commit", "-m", "now playing"], cwd=str(ROOT), check=False)
        subprocess.run(["git", "push", "origin", "master"], cwd=str(ROOT), check=False)
    except Exception:
        pass


async def poll_loop():
    global LAST_PUSH_KEY
    while True:
        await read_session()
        with state_lock:
            snapshot = dict(state)
        try:
            (ROOT / "docs" / "now-playing.json").write_text(json.dumps(snapshot), encoding="utf-8")
            key = json.dumps([
                snapshot.get("title"),
                snapshot.get("artist"),
                snapshot.get("album"),
                snapshot.get("playing"),
            ])
            if key != LAST_PUSH_KEY:
                LAST_PUSH_KEY = key
                _push_now_playing()
        except Exception:
            pass
        await asyncio.sleep(1.5)


def start_media_worker():
    def runner():
        asyncio.run(poll_loop())
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()


@app.get("/")
def home():
    return send_from_directory(ROOT / "templates", "index.html")


@app.get("/api/now-playing")
def now_playing():
    with state_lock:
        snapshot = dict(state)
    return jsonify(snapshot)


@app.get("/health")
def health():
    return jsonify({"ok": True, "winsdk_available": WINSDK_AVAILABLE})


if __name__ == "__main__":
    start_media_worker()
    print("\nSpotify Now Playing is starting.")
    print("Overlay URL: http://127.0.0.1:5055/")
    print("Keep this window open while streaming.\n")
    app.run(host="127.0.0.1", port=5055, debug=False, threaded=True)
