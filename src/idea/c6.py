"""
EcoLens - AI Waste Classifier
Hackathon Edition — Gemini 2.5 Flash + OpenCV + Flask (iPhone support)

Control from iPhone:
  1. Make sure iPhone and PC are on the same WiFi
  2. Run this script
  3. Open Safari on iPhone → go to http://YOUR_PC_IP:5000
  4. Tap SCAN button on your iPhone to trigger analysis
  5. Tap HISTORY tab to see all past scans + stats

Voice Commands (STRICT — only these exact words work):
  "scan"    → scan waste
  "save"    → save screenshot + log
  "clear"   → clear screen
  "history" → print history in terminal
  "quit"    → close app

Keyboard (on PC):
  SPACE → scan  |  S → save  |  C → clear  |  H → history  |  Q → quit

Install:
  pip install google-genai opencv-python pillow SpeechRecognition flask
  pip install pipwin
  pipwin install pyaudio
"""

import cv2
import io
import json
import datetime
import os
import threading
import queue
import subprocess
import socket
import speech_recognition as sr
from flask import Flask, Response, render_template_string, jsonify
from google import genai
from google.genai import types
from PIL import Image

# ─────────────────────────────────────────────
#  CONFIG  ← only edit these two lines
# ─────────────────────────────────────────────
API_KEY  = ""
CITY     = "Delhi"
LOG_FILE = "scan_history.json"

client = genai.Client(api_key=API_KEY)

# ─────────────────────────────────────────────
#  5R COLOR MAP (BGR for OpenCV)
# ─────────────────────────────────────────────
R_COLORS = {
    "Refuse":  (0,   60,  220),
    "Reduce":  (0,  165,  255),
    "Reuse":   (50, 200,   50),
    "Recycle": (255, 180,   0),
    "Rot":     (30,  140,  80),
    "Unknown": (120, 120, 120),
}

# ─────────────────────────────────────────────
#  STRICT VOICE COMMAND MAP
#  Only these exact spoken words are accepted.
#  Anything else is rejected with feedback.
# ─────────────────────────────────────────────
VOICE_COMMANDS = {
    "scan":    "scan",
    "save":    "save",
    "clear":   "clear",
    "history": "history",
    "quit":    "quit",
    "exit":    "quit",
}

# ─────────────────────────────────────────────
#  TEXT-TO-SPEECH via Windows PowerShell
# ─────────────────────────────────────────────
def speak(text):
    def _speak():
        clean = text.replace('"', '').replace("'", "")
        subprocess.Popen(
            ['powershell', '-Command',
             f'Add-Type -AssemblyName System.Speech; '
             f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
             f'$s.Rate = 2; '
             f'$s.Speak("{clean}")'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    threading.Thread(target=_speak, daemon=True).start()

# ─────────────────────────────────────────────
#  SHARED STATE
# ─────────────────────────────────────────────
command_queue = queue.Queue()
mic_status    = {"listening": False, "last_heard": "", "last_status": ""}
latest_frame  = {"img": None}
app_state     = {"results": [], "scan_time": "", "status": "Ready"}

# ─────────────────────────────────────────────
#  FLASK APP
# ─────────────────────────────────────────────
flask_app = Flask(__name__)

PHONE_UI = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="EcoLens">
  <title>EcoLens</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #0a0a0a; color: #fff;
      font-family: -apple-system, sans-serif;
      min-height: 100vh;
      display: flex; flex-direction: column; align-items: center;
      padding-bottom: 70px;
    }
    .header {
      width: 100%; background: #111;
      padding: 14px 20px;
      display: flex; align-items: center; justify-content: space-between;
      border-bottom: 1px solid #222;
      position: sticky; top: 0; z-index: 10;
    }
    .logo { font-size: 20px; font-weight: 700; color: #00e676; }
    .live-dot {
      width: 10px; height: 10px; background: #f44;
      border-radius: 50%; animation: blink 1s infinite;
    }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
    .tab-bar {
      position: fixed; bottom: 0; left: 0; right: 0;
      height: 62px; background: #111;
      border-top: 1px solid #222;
      display: flex; z-index: 100;
    }
    .tab {
      flex: 1; display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      gap: 4px; font-size: 11px; color: #555;
      cursor: pointer; transition: color 0.15s;
      -webkit-tap-highlight-color: transparent;
      padding-bottom: 4px;
    }
    .tab.active { color: #00e676; }
    .tab-icon { font-size: 22px; line-height: 1; }
    .page { display: none; width: 100%; max-width: 700px; }
    .page.active { display: flex; flex-direction: column; align-items: center; }
    .feed-wrap { width: 100%; background: #000; }
    .feed-wrap img { width: 100%; display: block; }
    .status-bar {
      width: 100%; background: #111;
      padding: 10px 16px; font-size: 13px; color: #aaa;
      border-top: 1px solid #222; min-height: 38px;
    }
    .status-bar span { color: #00e676; font-weight: 600; }
    .btn-row {
      display: flex; gap: 10px;
      padding: 14px 16px; width: 100%;
    }
    .btn {
      flex: 1; padding: 16px 6px;
      font-size: 14px; font-weight: 600;
      border: none; border-radius: 14px; cursor: pointer;
      transition: transform 0.1s, opacity 0.1s;
      -webkit-tap-highlight-color: transparent;
    }
    .btn:active { transform: scale(0.95); opacity: 0.85; }
    .btn-scan    { background: #00e676; color: #000; }
    .btn-save    { background: #2196F3; color: #fff; }
    .btn-clear   { background: #444;    color: #fff; }
    .btn-history { background: #7c3aed; color: #fff; }

    .voice-hint {
      width: 100%; background: #0d1a0d;
      border-top: 1px solid #1a3a1a;
      border-bottom: 1px solid #1a3a1a;
      padding: 8px 16px;
      font-size: 11px; color: #3a6a3a;
    }
    .voice-hint span { color: #00e676; font-weight: 700; }
    .voice-heard {
      width: 100%; background: #0a140a;
      padding: 7px 16px; font-size: 12px; color: #555;
      min-height: 30px; border-bottom: 1px solid #111;
    }
    .voice-heard .heard-ok  { color: #00e676; font-weight: 600; }
    .voice-heard .heard-bad { color: #f44336; font-weight: 600; }

    .results { width: 100%; padding: 0 16px 16px; }
    .result-card {
      background: #1a1a1a; border-radius: 12px;
      padding: 14px; margin-bottom: 10px;
      border-left: 4px solid #555;
    }
    .result-card.Recycle { border-left-color: #00bcd4; }
    .result-card.Reuse   { border-left-color: #4caf50; }
    .result-card.Rot     { border-left-color: #8bc34a; }
    .result-card.Refuse  { border-left-color: #f44336; }
    .result-card.Reduce  { border-left-color: #ff9800; }
    .cat-badge {
      display: inline-block; font-size: 11px; font-weight: 700;
      padding: 3px 10px; border-radius: 20px;
      margin-bottom: 6px; background: #333; color: #fff;
    }
    .item-name   { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
    .item-reason { font-size: 13px; color: #aaa; margin-bottom: 8px; }
    .section-label {
      font-size: 11px; font-weight: 600; color: #666;
      text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;
    }
    .idea-list { list-style: none; }
    .idea-list li {
      font-size: 13px; color: #ccc;
      padding: 3px 0 3px 16px; position: relative;
    }
    .idea-list li::before { content: "+"; position: absolute; left: 0; color: #00e676; }
    .local-tip {
      margin-top: 8px; font-size: 13px; color: #64b5f6;
      padding-left: 16px; position: relative;
    }
    .local-tip::before { content: "@"; position: absolute; left: 0; color: #64b5f6; }
    .empty-state {
      text-align: center; padding: 40px 20px;
      color: #444; font-size: 15px;
    }
    .empty-state .icon { font-size: 48px; margin-bottom: 12px; }

    /* ── HISTORY PAGE ── */
    .stats-row {
      display: grid; grid-template-columns: repeat(3, 1fr);
      gap: 10px; padding: 16px 16px 8px; width: 100%;
    }
    .stat-card {
      background: #1a1a1a; border-radius: 10px;
      padding: 12px 10px; text-align: center;
    }
    .stat-number { font-size: 22px; font-weight: 700; color: #00e676; }
    .stat-label  { font-size: 11px; color: #555; margin-top: 2px; }
    .history-header {
      width: 100%;
      display: flex; align-items: center; justify-content: space-between;
      padding: 8px 16px;
    }
    .history-title { font-size: 18px; font-weight: 700; }
    .clear-btn {
      font-size: 13px; color: #f44336;
      background: none; border: none; cursor: pointer; padding: 6px 10px;
    }
    .history-list { width: 100%; padding: 0 16px 16px; }
    .h-entry {
      background: #1a1a1a; border-radius: 12px;
      margin-bottom: 12px; overflow: hidden;
    }
    .h-entry-head {
      display: flex; align-items: center; justify-content: space-between;
      padding: 12px 14px; cursor: pointer;
      -webkit-tap-highlight-color: transparent;
    }
    .h-entry-head:active { background: #222; }
    .h-ts      { font-size: 13px; font-weight: 600; color: #00e676; }
    .h-summary { font-size: 12px; color: #555; margin-top: 3px; }
    .h-chevron { font-size: 18px; color: #444; transition: transform 0.2s; }
    .h-chevron.open { transform: rotate(90deg); }
    .h-items {
      display: none; padding: 0 14px 14px;
      border-top: 1px solid #222;
    }
    .h-items.open { display: block; }
    .h-item-row {
      display: flex; align-items: center; gap: 10px;
      padding: 8px 0; border-bottom: 1px solid #1f1f1f;
    }
    .h-item-row:last-child { border-bottom: none; }
    .h-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
    .d-Recycle { background: #00bcd4; }
    .d-Reuse   { background: #4caf50; }
    .d-Rot     { background: #8bc34a; }
    .d-Refuse  { background: #f44336; }
    .d-Reduce  { background: #ff9800; }
    .d-Unknown { background: #555; }
    .h-item-name { font-size: 13px; color: #ccc; flex: 1; }
    .h-item-cat  { font-size: 11px; color: #666; }
    .h-idea      { font-size: 11px; color: #555; margin-top: 2px; }
    .no-history {
      text-align: center; padding: 60px 20px;
      color: #333; font-size: 15px;
    }
    .no-history .icon { font-size: 40px; margin-bottom: 12px; }
  </style>
</head>
<body>

  <div class="header">
    <span class="logo">EcoLens</span>
    <div class="live-dot"></div>
  </div>

  <!-- SCAN PAGE -->
  <div class="page active" id="page-scan">
    <div class="feed-wrap">
      <img src="/feed" id="stream" />
    </div>

    <div class="status-bar" id="status">
      <span>Ready</span> — tap Scan to analyze waste
    </div>

    <div class="btn-row">
      <button class="btn btn-scan"    onclick="doCommand('scan')">SCAN</button>
      <button class="btn btn-save"    onclick="doCommand('save')">SAVE</button>
      <button class="btn btn-clear"   onclick="doCommand('clear')">CLEAR</button>
      <button class="btn btn-history" onclick="showTab('history')">HISTORY</button>
    </div>

    <!-- Voice hint strip -->
    <div class="voice-hint">
      Voice: <span>scan</span> &nbsp;|&nbsp; <span>save</span> &nbsp;|&nbsp;
      <span>clear</span> &nbsp;|&nbsp; <span>history</span> &nbsp;|&nbsp; <span>quit</span>
    </div>
    <div class="voice-heard" id="voice-heard">Listening for voice commands...</div>

    <div class="results" id="results">
      <div class="empty-state">
        <div class="icon">&#9851;</div>
        Point the PC camera at waste<br>and tap SCAN
      </div>
    </div>
  </div>

  <!-- HISTORY PAGE -->
  <div class="page" id="page-history">
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-number" id="stat-scans">0</div>
        <div class="stat-label">Total scans</div>
      </div>
      <div class="stat-card">
        <div class="stat-number" id="stat-items">0</div>
        <div class="stat-label">Items found</div>
      </div>
      <div class="stat-card">
        <div class="stat-number" id="stat-recycle">0</div>
        <div class="stat-label">Recyclable</div>
      </div>
    </div>
    <div class="history-header">
      <span class="history-title">Scan History</span>
      <button class="clear-btn" onclick="clearHistory()">Clear all</button>
    </div>
    <div class="history-list" id="history-list">
      <div class="no-history">
        <div class="icon">&#128193;</div>
        No scans saved yet.<br>Tap SAVE after a scan.
      </div>
    </div>
  </div>

  <!-- BOTTOM TAB BAR -->
  <div class="tab-bar">
    <div class="tab active" id="tab-scan" onclick="showTab('scan')">
      <span class="tab-icon">&#128247;</span>
      Scan
    </div>
    <div class="tab" id="tab-history" onclick="showTab('history')">
      <span class="tab-icon">&#128193;</span>
      History
    </div>
  </div>

  <script>
    function showTab(name) {
      document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.getElementById('page-' + name).classList.add('active');
      document.getElementById('tab-'  + name).classList.add('active');
      if (name === 'history') loadHistory();
    }

    function doCommand(cmd) {
      fetch('/cmd/' + cmd)
        .then(r => r.json())
        .then(d => {
          document.getElementById('status').innerHTML =
            '<span>' + d.status + '</span>';
        });
    }

    // Poll voice status every second — shows what was heard on iPhone
    function pollVoice() {
      fetch('/voice_status')
        .then(r => r.json())
        .then(d => {
          const el = document.getElementById('voice-heard');
          if (!d.last_heard) {
            el.innerHTML = 'Listening for voice commands...';
            return;
          }
          if (d.last_status === 'ok') {
            el.innerHTML = 'Heard: <span class="heard-ok">"' + d.last_heard + '"</span> ✓ command accepted';
          } else {
            el.innerHTML = 'Heard: <span class="heard-bad">"' + d.last_heard + '"</span> ✗ invalid — use: scan, save, clear, history, quit';
          }
        })
        .catch(() => {});
    }
    setInterval(pollVoice, 1000);

    function refreshResults() {
      fetch('/results')
        .then(r => r.json())
        .then(data => {
          if (!data.results || data.results.length === 0) return;
          renderCards(data.results, document.getElementById('results'));
          document.getElementById('status').innerHTML =
            '<span>Scanned at ' + data.scan_time + '</span> — ' +
            data.results.length + ' item(s) found';
        });
    }
    setInterval(refreshResults, 2000);

    function renderCards(results, container) {
      container.innerHTML = '';
      results.forEach(item => {
        const cat    = item.category    || 'Unknown';
        const name   = item.item        || 'Item';
        const reason = item.reason      || '';
        const ideas  = item.reuse_ideas || [];
        const tip    = item.local_tip   || '';
        const card   = document.createElement('div');
        card.className = 'result-card ' + cat;
        card.innerHTML =
          '<div class="cat-badge">' + cat + '</div>' +
          '<div class="item-name">'   + name   + '</div>' +
          '<div class="item-reason">' + reason + '</div>' +
          (ideas.length ?
            '<div class="section-label">Reuse ideas</div>' +
            '<ul class="idea-list">' + ideas.map(i => '<li>' + i + '</li>').join('') + '</ul>'
            : '') +
          (tip ? '<div class="local-tip">' + tip + '</div>' : '');
        container.appendChild(card);
      });
    }

    function loadHistory() {
      fetch('/history')
        .then(r => r.json())
        .then(data => {
          const entries = data.history || [];
          const list    = document.getElementById('history-list');

          let totalItems = 0, totalRecycle = 0;
          entries.forEach(e => {
            (e.results || []).forEach(item => {
              totalItems++;
              if (item.category === 'Recycle') totalRecycle++;
            });
          });
          document.getElementById('stat-scans').textContent   = entries.length;
          document.getElementById('stat-items').textContent   = totalItems;
          document.getElementById('stat-recycle').textContent = totalRecycle;

          if (entries.length === 0) {
            list.innerHTML =
              '<div class="no-history"><div class="icon">&#128193;</div>' +
              'No scans saved yet.<br>Tap SAVE after a scan.</div>';
            return;
          }

          list.innerHTML = '';
          [...entries].reverse().forEach(entry => {
            const results = entry.results || [];
            const ts      = entry.timestamp || '';
            const readable = ts.length === 15
              ? ts.slice(0,4)+'/'+ts.slice(4,6)+'/'+ts.slice(6,8)
                +' '+ts.slice(9,11)+':'+ts.slice(11,13)+':'+ts.slice(13,15)
              : ts;

            const cats    = [...new Set(results.map(r => r.category || 'Unknown'))];
            const summary = results.length + ' item' +
              (results.length !== 1 ? 's' : '') + ' — ' + cats.join(', ');

            const itemsHtml = results.map(item => {
              const cat  = item.category || 'Unknown';
              const name = item.item     || 'Item';
              const idea = (item.reuse_ideas || [''])[0];
              return '<div class="h-item-row">' +
                '<div class="h-dot d-' + cat + '"></div>' +
                '<div class="h-item-name">' + name +
                  (idea ? '<div class="h-idea">' + idea + '</div>' : '') +
                '</div>' +
                '<div class="h-item-cat">' + cat + '</div>' +
              '</div>';
            }).join('');

            const el = document.createElement('div');
            el.className = 'h-entry';
            el.innerHTML =
              '<div class="h-entry-head" onclick="toggleEntry(this)">' +
                '<div>' +
                  '<div class="h-ts">' + readable + '</div>' +
                  '<div class="h-summary">' + summary + '</div>' +
                '</div>' +
                '<div class="h-chevron">&#8250;</div>' +
              '</div>' +
              '<div class="h-items">' + itemsHtml + '</div>';
            list.appendChild(el);
          });
        });
    }

    function toggleEntry(header) {
      const items   = header.nextElementSibling;
      const chevron = header.querySelector('.h-chevron');
      const isOpen  = items.classList.contains('open');
      items.classList.toggle('open',   !isOpen);
      chevron.classList.toggle('open', !isOpen);
    }

    function clearHistory() {
      if (!confirm('Clear all scan history?')) return;
      fetch('/history/clear', { method: 'POST' })
        .then(() => loadHistory());
    }
  </script>
</body>
</html>
"""

# ─────────────────────────────────────────────
#  FLASK ROUTES
# ─────────────────────────────────────────────
@flask_app.route("/")
def index():
    return render_template_string(PHONE_UI)

@flask_app.route("/feed")
def feed():
    def generate():
        while True:
            if latest_frame["img"] is not None:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                       + latest_frame["img"] + b"\r\n")
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@flask_app.route("/cmd/<cmd>")
def command(cmd):
    if cmd in ["scan", "save", "clear", "history", "quit"]:
        command_queue.put(cmd)
        messages = {
            "scan":    "Scanning...",
            "save":    "Saving...",
            "clear":   "Cleared",
            "history": "Loading history...",
            "quit":    "Closing..."
        }
        return jsonify({"status": messages.get(cmd, "OK")})
    return jsonify({"status": "Unknown command"})

@flask_app.route("/results")
def results():
    return jsonify({
        "results":   app_state["results"],
        "scan_time": app_state["scan_time"],
        "status":    app_state["status"]
    })

@flask_app.route("/history")
def history():
    entries = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            entries = json.load(f)
    return jsonify({"history": entries})

@flask_app.route("/history/clear", methods=["POST"])
def clear_history():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    return jsonify({"status": "cleared"})

@flask_app.route("/voice_status")
def voice_status():
    return jsonify({
        "last_heard":  mic_status["last_heard"],
        "last_status": mic_status["last_status"]
    })

# ─────────────────────────────────────────────
#  VOICE LISTENER — STRICT MODE
#  Only exact words from VOICE_COMMANDS work.
#  Everything else is rejected with feedback.
# ─────────────────────────────────────────────
def voice_listener():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold         = 400
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold          = 0.6

    valid = "scan, save, clear, history, quit"

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            mic_status["listening"] = True
            print(f"\n  Voice ready (STRICT MODE)")
            print(f"  Valid commands: {valid}\n")
            speak(f"Voice ready. Say: {valid}")

            while True:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    text  = recognizer.recognize_google(audio).lower().strip()

                    # Take only the first word, strip punctuation
                    first_word = text.split()[0].rstrip('.,!?') if text.split() else ""

                    if first_word in VOICE_COMMANDS:
                        cmd = VOICE_COMMANDS[first_word]
                        mic_status["last_heard"]  = first_word
                        mic_status["last_status"] = "ok"
                        print(f"  Voice OK  '{first_word}' → {cmd}")
                        command_queue.put(cmd)
                    else:
                        # Reject anything not in the allowed list
                        mic_status["last_heard"]  = text[:30]
                        mic_status["last_status"] = "rejected"
                        print(f"  Voice BAD '{text}' — not valid. Use: {valid}")
                        speak(f"Invalid. Say: {valid}")

                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"  Speech API error: {e}")
                    mic_status["listening"] = False
                    break

    except Exception as e:
        mic_status["listening"] = False
        print(f"  Mic unavailable: {e}")
        print("  Keyboard + iPhone controls still work.\n")

# ─────────────────────────────────────────────
#  GEMINI PROMPT
# ─────────────────────────────────────────────
PROMPT = f"""
You are EcoLens, an expert waste management AI.
Analyze this image and identify EVERY visible waste or recyclable item.

Return a JSON array only (no markdown, pure JSON):
[
  {{
    "item": "Plastic water bottle",
    "category": "Recycle",
    "reason": "PET plastic, widely accepted",
    "reuse_ideas": ["Refill as water bottle", "Cut into a plant pot", "Store small items"],
    "where_to_dispose": ["MRF facility", "Supermarket drop-off", "Blue municipal bin"],
    "local_tip": "Drop at nearest NDMC blue bin or Kabadiwala in {CITY}"
  }}
]

Rules:
- category must be exactly one of: Refuse, Reduce, Reuse, Recycle, Rot
- reuse_ideas: 3 creative suggestions
- where_to_dispose: 3 real facility types
- local_tip: one specific actionable tip for {CITY}
- List EVERY visible item separately
- Return ONLY the JSON array
"""

# ─────────────────────────────────────────────
#  DRAW OVERLAY
# ─────────────────────────────────────────────
def draw_overlay(frame, results, scan_time, mic_on):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    panel_x = w - 430

    cv2.rectangle(overlay, (panel_x, 0), (w, h), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)

    cv2.rectangle(frame, (panel_x, 0), (w, 52), (20, 20, 20), -1)
    cv2.putText(frame, "EcoLens  AI Waste Scanner",
                (panel_x + 12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 230, 120), 2)
    cv2.putText(frame, f"Scan: {scan_time}",
                (panel_x + 12, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

    y = 95
    for i, item in enumerate(results):
        if y > h - 80:
            cv2.putText(frame, f"  ... +{len(results)-i} more items",
                        (panel_x + 12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (130, 130, 130), 1)
            break

        cat    = item.get("category", "Unknown")
        color  = R_COLORS.get(cat, R_COLORS["Unknown"])
        name   = item.get("item", "Item")
        reason = item.get("reason", "")

        cv2.rectangle(frame, (panel_x + 8, y - 2), (panel_x + 115, y + 20), color, -1)
        cv2.putText(frame, cat,       (panel_x + 14,  y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (255, 255, 255), 1)
        cv2.putText(frame, name[:28], (panel_x + 124, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5,  (235, 235, 235), 1)
        y += 26
        cv2.putText(frame, reason[:50], (panel_x + 12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (160, 200, 160), 1)
        y += 18

        for idea in item.get("reuse_ideas", [])[:2]:
            cv2.putText(frame, f"  + {idea[:46]}", (panel_x + 12, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (80, 220, 100), 1)
            y += 16

        tip = item.get("local_tip", "")
        if tip:
            cv2.putText(frame, f"  @ {str(tip)[:46]}", (panel_x + 12, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 180, 255), 1)
            y += 18

        cv2.line(frame, (panel_x + 8, y + 2), (w - 8, y + 2), (45, 45, 45), 1)
        y += 14

    # Bottom bar — keyboard shortcuts + voice commands
    cv2.rectangle(frame, (0, h - 52), (panel_x - 1, h), (12, 12, 12), -1)
    cv2.putText(frame, "SPACE:scan  S:save  C:clear  H:history  Q:quit",
                (10, h - 32), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (70, 70, 70), 1)
    cv2.putText(frame, "VOICE: scan | save | clear | history | quit",
                (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38,
                (0, 160, 60) if mic_on else (60, 60, 100), 1)

    # Last heard indicator on overlay
    last   = mic_status.get("last_heard", "")
    status = mic_status.get("last_status", "")
    if last:
        c = (0, 200, 80) if status == "ok" else (0, 80, 220)
        cv2.putText(frame, f"Heard: '{last}'",
                    (panel_x + 12, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.36, c, 1)

    cv2.circle(frame, (20, 22), 7, (0, 0, 220), -1)
    cv2.putText(frame, "LIVE", (33, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 80, 220), 1)
    if mic_on:
        cv2.circle(frame, (panel_x - 20, 22), 7, (0, 200, 80), -1)
        cv2.putText(frame, "MIC", (panel_x - 50, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 80), 1)

    return frame

# ─────────────────────────────────────────────
#  ANALYZE FRAME
# ─────────────────────────────────────────────
def analyze_frame(frame):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            PROMPT,
            types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")
        ]
    )

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ─────────────────────────────────────────────
#  SAVE LOG
# ─────────────────────────────────────────────
def save_log(results, frame):
    ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = f"scan_{ts}.jpg"
    cv2.imwrite(img_name, frame)

    history = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            history = json.load(f)
    history.append({"timestamp": ts, "image": img_name, "results": results})
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)

    print(f"  Saved: {img_name}  |  Log: {LOG_FILE}")
    speak("Scan saved.")

# ─────────────────────────────────────────────
#  PRINT HISTORY IN TERMINAL
# ─────────────────────────────────────────────
def print_history():
    if not os.path.exists(LOG_FILE):
        print("\n  No scan history found.\n")
        speak("No history found.")
        return

    with open(LOG_FILE) as f:
        entries = json.load(f)

    if not entries:
        print("\n  History is empty.\n")
        speak("History is empty.")
        return

    TERM = {
        "Recycle": "\033[96m", "Reuse":  "\033[92m",
        "Rot":     "\033[32m", "Refuse": "\033[91m", "Reduce": "\033[93m"
    }

    print("\n" + "="*58)
    print(f"   EcoLens History — {len(entries)} scan(s)")
    print("="*58)
    for entry in reversed(entries):
        ts = entry.get("timestamp", "")
        readable = (ts[:4]+"/"+ts[4:6]+"/"+ts[6:8]+" "+ts[9:11]+":"+ts[11:13]
                    if len(ts) == 15 else ts)
        results = entry.get("results", [])
        print(f"\n  [{readable}]  {len(results)} item(s)")
        for item in results:
            cat  = item.get("category", "?")
            name = item.get("item", "?")
            col  = TERM.get(cat, "\033[0m")
            print(f"    {col}[{cat}]\033[0m  {name}")
    print("="*58 + "\n")
    speak(f"History has {len(entries)} saved scans.")

# ─────────────────────────────────────────────
#  SPEAK RESULTS
# ─────────────────────────────────────────────
def speak_results(results):
    if not results:
        speak("No items detected.")
        return
    lines = []
    for item in results[:4]:
        name = item.get("item", "item")
        cat  = item.get("category", "unknown")
        idea = item.get("reuse_ideas", [""])[0]
        lines.append(f"{name}: {cat}. {idea}.")
    summary = " ".join(lines)
    if len(results) > 4:
        summary += f" And {len(results)-4} more items."
    speak(summary)

# ─────────────────────────────────────────────
#  PRINT RESULTS
# ─────────────────────────────────────────────
def print_results(results):
    TERM = {
        "Recycle": "\033[96m", "Reuse":  "\033[92m",
        "Rot":     "\033[32m", "Refuse": "\033[91m", "Reduce": "\033[93m"
    }
    print("\n" + "="*58)
    print("   EcoLens  — Waste Analysis")
    print("="*58)
    for item in results:
        cat  = item.get("category", "?")
        name = item.get("item", "?")
        col  = TERM.get(cat, "\033[0m")
        print(f"\n  {col}[ {cat} ]\033[0m  {name}")
        print(f"  Reason  : {item.get('reason','')}")
        print(f"  Reuse   : {' | '.join(item.get('reuse_ideas', []))}")
        print(f"  Dispose : {' | '.join(item.get('where_to_dispose', []))}")
        print(f"  {CITY} tip : {item.get('local_tip','')}")
    print("="*58 + "\n")

# ─────────────────────────────────────────────
#  DO SCAN
# ─────────────────────────────────────────────
def do_scan(frame, state):
    speak("Scanning now.")
    app_state["status"] = "Scanning..."
    print("  Analyzing image...")
    try:
        results = analyze_frame(frame)
        state["results"]       = results
        state["scan_time"]     = datetime.datetime.now().strftime("%H:%M:%S")
        app_state["results"]   = results
        app_state["scan_time"] = state["scan_time"]
        app_state["status"]    = f"Found {len(results)} item(s)"
        print_results(results)
        speak_results(results)
    except json.JSONDecodeError as e:
        print(f"  Parse error: {e}")
        speak("Could not read response. Try again.")
        app_state["status"] = "Parse error — try again"
    except Exception as e:
        print(f"  Error: {e}")
        speak("An error occurred.")
        app_state["status"] = "Error — try again"

# ─────────────────────────────────────────────
#  GET LOCAL IP
# ─────────────────────────────────────────────
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("  Could not open webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    threading.Thread(target=voice_listener, daemon=True).start()
    threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=5000,
                                     debug=False, use_reloader=False),
        daemon=True
    ).start()

    local_ip = get_local_ip()
    speak("EcoLens started.")

    print("\n" + "="*55)
    print("  EcoLens started!")
    print(f"\n  iPhone : open Safari → http://{local_ip}:5000")
    print(f"  PC     : keyboard or voice commands")
    print(f"\n  Voice  : scan | save | clear | history | quit")
    print(f"  Keys   : SPACE=scan  S=save  C=clear  H=history  Q=quit")
    print("="*55 + "\n")

    state         = {"results": [], "scan_time": ""}
    display_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        show   = frame.copy()
        mic_on = mic_status["listening"]

        if state["results"]:
            show = draw_overlay(show, state["results"], state["scan_time"], mic_on)
        else:
            cv2.putText(show, "EcoLens  —  Say 'scan' or press SPACE",
                        (30, 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 230, 120), 2)
            cv2.putText(show, "Point camera at any waste item or mixed pile",
                        (30, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 160, 160), 1)
            cv2.putText(show, f"iPhone: http://{local_ip}:5000",
                        (30, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 180, 255), 1)
            cv2.putText(show, "Voice: scan | save | clear | history | quit",
                        (30, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 140, 60), 1)

        _, buf = cv2.imencode(".jpg", show, [cv2.IMWRITE_JPEG_QUALITY, 70])
        latest_frame["img"] = buf.tobytes()

        cv2.imshow("EcoLens - AI Waste Classifier", show)
        display_frame = show

        # ── Voice / button commands ──
        try:
            cmd = command_queue.get_nowait()
            if cmd == "scan":
                do_scan(frame, state)
            elif cmd == "save" and state["results"]:
                save_log(state["results"], display_frame)
            elif cmd == "clear":
                state["results"]     = []
                state["scan_time"]   = ""
                app_state["results"] = []
                speak("Cleared.")
            elif cmd == "history":
                print_history()
            elif cmd == "quit":
                speak("Goodbye.")
                break
        except queue.Empty:
            pass

        # ── Keyboard ──
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            do_scan(frame, state)
        elif key == ord('s') and state["results"]:
            save_log(state["results"], display_frame)
        elif key == ord('c'):
            state["results"]     = []
            state["scan_time"]   = ""
            app_state["results"] = []
        elif key == ord('h'):
            print_history()
        elif key == ord('q'):
            speak("Goodbye.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n  EcoLens closed.\n")

if __name__ == "__main__":
    main()
