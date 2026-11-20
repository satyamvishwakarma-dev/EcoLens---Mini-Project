"""
EcoLens Backend Server (Flask + OpenCV + Non-Blocking AI + Strict Voice + Safe TTS).
Serves the desktop website from src/frontend/ and exposes REST & MJPEG endpoints.
"""
import base64
import datetime
import json
import os
import socket
import subprocess
import threading
import time

import cv2
from flask import Flask, Response, jsonify, request, send_from_directory

from ecolens_mini_project.ai_engine import EcoLensAI
from ecolens_mini_project.config import (
    DEFAULT_CITY,
    FRONTEND_DIR,
    LOG_FILE,
    SCANS_DIR,
    VOICE_COMMANDS,
)

# Optional voice recognition import (graceful fallback if PyAudio isn't installed)
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# ─────────────────────────────────────────────
#  FLASK APP & SHARED STATE
# ─────────────────────────────────────────────
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
ai_engine = EcoLensAI()

state_lock = threading.Lock()
is_speaking = threading.Event()  # Pauses mic while TTS speaks to prevent echo loops

app_state = {
    "results": [],
    "scan_time": "",
    "status": "Ready",
    "is_scanning": False,
    "city": DEFAULT_CITY,
}

mic_status = {
    "listening": False,
    "last_heard": "",
    "last_status": "",
}

camera_state = {
    "frame_bgr": None,
    "jpeg_bytes": None,
    "active": False,
}


# ─────────────────────────────────────────────
#  SAFE POWERSHELL TEXT-TO-SPEECH (UTF-16LE Base64)
# ─────────────────────────────────────────────
def speak(text: str):
    """Speaks text asynchronously on Windows without shell-escaping vulnerabilities."""
    def _worker():
        is_speaking.set()
        try:
            clean = text.replace('"', "").replace("'", "").replace("\n", " ")
            ps_script = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$s.Rate = 2; "
                f'$s.Speak("{clean}")'
            )
            encoded = base64.b64encode(ps_script.encode("utf-16-le")).decode("ascii")
            subprocess.run(
                ["powershell", "-NoProfile", "-EncodedCommand", encoded],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        finally:
            time.sleep(0.4)
            is_speaking.clear()

    threading.Thread(target=_worker, daemon=True).start()


# ─────────────────────────────────────────────
#  BACKGROUND WEBCAM CAPTURE THREAD
# ─────────────────────────────────────────────
def camera_loop():
    """Continuously captures webcam frames in the background at ~30 FPS."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("  [WARN] No webcam detected. Image upload mode still works.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera_state["active"] = True

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        with state_lock:
            camera_state["frame_bgr"] = frame
            camera_state["jpeg_bytes"] = buf.tobytes()

        time.sleep(0.03)  # Cap at ~30 FPS to save CPU


# ─────────────────────────────────────────────
#  CORE ACTIONS (SCAN / SAVE / CLEAR)
# ─────────────────────────────────────────────
def trigger_scan(image_bytes: bytes | None = None, city: str | None = None):
    """Runs Gemini vision analysis in a background thread so video never freezes."""
    with state_lock:
        if app_state["is_scanning"]:
            return
        app_state["is_scanning"] = True
        app_state["status"] = "Analyzing with Gemini 2.5 Flash..."
        target_city = city or app_state["city"]
        if image_bytes is None:
            image_bytes = camera_state["jpeg_bytes"]

    if not image_bytes:
        with state_lock:
            app_state["is_scanning"] = False
            app_state["status"] = "No camera frame available"
        return

    def _worker():
        speak("Scanning now.")
        try:
            results = ai_engine.analyze_image_bytes(image_bytes, city=target_city)
            now = datetime.datetime.now().strftime("%H:%M:%S")
            with state_lock:
                app_state["results"] = results
                app_state["scan_time"] = now
                app_state["status"] = f"Found {len(results)} item(s)"
            if results:
                summary = ". ".join(
                    f"{r['item']}: {r['category']}" for r in results[:3]
                )
                speak(summary)
            else:
                speak("No waste items detected.")
        except Exception as exc:
            print(f"  [ERROR] Scan failed: {exc}")
            with state_lock:
                app_state["status"] = f"Scan error: {exc}"
            speak("Scan failed. Please try again.")
        finally:
            with state_lock:
                app_state["is_scanning"] = False

    threading.Thread(target=_worker, daemon=True).start()


def save_current_scan() -> bool:
    """Saves the latest scan results and snapshot to scan_history.json."""
    with state_lock:
        results = list(app_state["results"])
        frame = camera_state["frame_bgr"].copy() if camera_state["frame_bgr"] is not None else None
        city = app_state["city"]

    if not results:
        return False

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = f"scan_{ts}.jpg"
    if frame is not None:
        cv2.imwrite(str(SCANS_DIR / img_name), frame)

    history = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    history.append({
        "timestamp": ts,
        "city": city,
        "image": img_name,
        "results": results,
    })

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    speak("Scan saved.")
    return True


# ─────────────────────────────────────────────
#  STRICT VOICE LISTENER THREAD
# ─────────────────────────────────────────────
def voice_listener():
    """Listens for exact voice commands while ignoring TTS playback."""
    if not VOICE_AVAILABLE:
        return

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.6

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            mic_status["listening"] = True
            print("  [VOICE] Strict mode active: scan | save | clear | history | quit")

            while True:
                if is_speaking.is_set():
                    time.sleep(0.2)
                    continue
                try:
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=3)
                    if is_speaking.is_set():
                        continue

                    text = recognizer.recognize_google(audio).lower().strip()
                    first_word = text.split()[0].rstrip(".,!?") if text.split() else ""

                    if first_word in VOICE_COMMANDS:
                        cmd = VOICE_COMMANDS[first_word]
                        mic_status["last_heard"] = first_word
                        mic_status["last_status"] = "ok"
                        if cmd == "scan":
                            trigger_scan()
                        elif cmd == "save":
                            save_current_scan()
                        elif cmd == "clear":
                            with state_lock:
                                app_state["results"] = []
                                app_state["scan_time"] = ""
                                app_state["status"] = "Cleared"
                            speak("Cleared.")
                    else:
                        mic_status["last_heard"] = text[:30]
                        mic_status["last_status"] = "rejected"
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    pass
                except sr.RequestError:
                    mic_status["listening"] = False
                    break
    except Exception as exc:
        mic_status["listening"] = False
        print(f"  [VOICE] Mic unavailable ({exc}). Web controls still work.")


# ─────────────────────────────────────────────
#  FLASK ROUTES (FRONTEND + API)
# ─────────────────────────────────────────────
@app.route("/")
def serve_index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.route("/feed")
def video_feed():
    def generate():
        while True:
            with state_lock:
                frame_bytes = camera_state["jpeg_bytes"]
            if frame_bytes:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
            time.sleep(0.033)  # ~30 FPS throttle

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/scan", methods=["POST"])
def api_scan():
    city = request.form.get("city") or (request.json.get("city") if request.is_json else None)
    if city:
        with state_lock:
            app_state["city"] = city

    # Support either uploaded image file OR live webcam capture
    if "image" in request.files:
        image_bytes = request.files["image"].read()
        trigger_scan(image_bytes=image_bytes, city=city)
    else:
        trigger_scan(city=city)

    return jsonify({"status": "Scanning started"})


@app.route("/api/save", methods=["POST"])
def api_save():
    saved = save_current_scan()
    return jsonify({"saved": saved, "status": "Saved to history" if saved else "Nothing to save"})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    with state_lock:
        app_state["results"] = []
        app_state["scan_time"] = ""
        app_state["status"] = "Ready"
    return jsonify({"status": "Cleared"})


@app.route("/api/results")
def api_results():
    with state_lock:
        return jsonify({
            "results": app_state["results"],
            "scan_time": app_state["scan_time"],
            "status": app_state["status"],
            "is_scanning": app_state["is_scanning"],
            "camera_active": camera_state["active"],
        })


@app.route("/api/history", methods=["GET", "DELETE"])
def api_history():
    if request.method == "DELETE":
        if LOG_FILE.exists():
            os.remove(LOG_FILE)
        return jsonify({"status": "cleared"})

    entries = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            entries = json.load(f)
    return jsonify({"history": entries})


@app.route("/api/voice_status")
def api_voice_status():
    return jsonify(mic_status)


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run():
    """Entry point for `uv run ecolens`."""
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=voice_listener, daemon=True).start()

    ip = get_local_ip()
    print("\n" + "=" * 56)
    print("  EcoLens Web Server Running!")
    print(f"  Desktop : http://localhost:5000")
    print(f"  Network : http://{ip}:5000")
    print("=" * 56 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    run()