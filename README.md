# EcoLens - AI Waste Classifier & 5R Circular Assistant

![EcoLens Banner](https://img.shields.io/badge/EcoLens-AI%20Waste%20Classifier-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-AI%20Vision-orange?style=for-the-badge)

## 📃 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Voice Commands](#-voice-commands)
- [Project Structure](#-project-structure)
---

## 📖 Overview

**EcoLens** is a full-stack web application that classifies waste items using Google's Gemini AI vision model, provides detailed 5R (Refuse, Reduce, Reuse, Recycle, Rot) circular economy guidance, and offers localized disposal recommendations based on city-specific municipal rules.

Users can scan waste via live webcam, upload photos, or use strict voice commands hands-free. The application stores scan history, tracks impact metrics, and provides an interactive 5R framework guide.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Live Webcam Scanning** | Real-time waste classification from webcam feed |
| **Image Upload** | Upload JPEG/PNG images for analysis |
| **Voice Commands** | Hands-free control: `scan`, `save`, `clear`, `history`, `quit` |
| **5R Classification** | Automatic categorization into Refuse, Reduce, Reuse, Recycle, Rot |
| **Gemini AI Vision** | Google Gemini 4.0 Hydrogen with structured JSON output |
| **2D Bounding Boxes** | Normalized bounding boxes [ymin, xmin, ymax, xmax] scaled 0-1000 |
| **Localized Guidance** | City-specific disposal tips (currently: Delhi, Greater Noida, Mumbai, Bengaluru) |
| **Scan History** | Persisted scan history with impact metrics (CO₂e saved estimates) |
| **Responsive UI** | Modern dark-themed interface built with Tailwind CSS |
| **Multilingual Support** | City selector with regional disposal guidance |

---

## 🔧 Prerequisites

- **Python** >= 3.11
- **Google Gemini API key** - obtain from [Google AI Studio](https://ai.google.dev/)
- **Git** (optional, for cloning)

The following system dependencies are required for full functionality:
- Webcam access (for live scanning)
- Microphone access (for voice commands)
- [Optional] PyAudio for speech recognition

---

## 🛠️ Installation

1. **Clone the repository** (or download the project files):

```bash
git clone https://github.com/your-username/EcoLens-Mini-Project.git
cd EcoLens-Mini-Project
```

2. **Create a virtual environment** (recommended):

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. **Install dependencies**:

```bash
pip install -r pyproject.toml
# Or using uv:
uv sync
```

4. **Set up environment variables**:

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_CITY=Delhi
MODEL_NAME=gemini-3.5-flash-lite
```

> ⚠️ **Never commit `.env` to version control.** It is listed in `.gitignore`.

5. **Ensure the `saved_scans` directory exists** (created automatically on first run).

---

## ⚙️ Configuration

Configuration is managed in `src/ecolens_mini_project/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | _(required)_ | Google Gemini API key |
| `DEFAULT_CITY` | `"Delhi"` | Default city for localized disposal tips |
| `MODEL_NAME` | `"gemini-3.5-flash-lite"` | Primary Gemini model |
| `PROJECT_ROOT` | Auto-detected | Repository root directory |
| `FRONTEND_DIR` | `src/frontend/` | Frontend static files directory |
| `SCANS_DIR` | `saved_scans/` | Directory for storing scan snapshots |
| `LOG_FILE` | `scan_history.json` | Persisted scan history file |

**Supported cities** for localized tips: `Delhi`, `Greater Noida`, `Mumbai`, `Bengaluru`

To add a new city, update:
- `src/frontend/index.html` - city selector options
- `src/ecolens_mini_project/config.py` - `DEFAULT_CITY` and VOICE_COMMANDS if needed
- `src/ecolens_mini_project/ai_engine.py` - prompt city reference

---

## ▶️ Running the Application

### Development Mode

```bash
python -m src.ecolens_mini_project.main
# Or directly:
python src/ecolens_mini_project/main.py
```

### Using UV

```bash
uv run ecolens
# (registered as entry point ecolens = "ecolens_mini_project.main:run")
```

### Production Mode (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.ecolens_mini_project.main:app
```

### Access the Application

Open your browser at:

- **Local**: `http://localhost:5000`
- **Network**: `http://<your-ip>:5000` (find IP with `ip addr` or the app prints it)

The terminal will display:

```
  EcoLens Web Server Running!
  Desktop : http://localhost:5000
  Network : http://192.168.1.42:5000
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the frontend index.html |
| `/feed` | GET | MJPEG webcam video stream |
| `/api/scan` | POST | Trigger image analysis (JSON body or form-data with `image` file + optional `city`) |
| `/api/save` | POST | Save current scan results to history |
| `/api/clear` | POST | Clear current results and scan state |
| `/api/results` | GET | Get current classification results |
| `/api/history` | GET/DELETE | Retrieve or clear scan history |
| `/api/voice_status` | GET | Get microphone/voice listener status |

### Example: `/api/scan`

```bash
curl -X POST http://localhost:5000/api/scan \
  -F "image=@photo.jpg" \
  -F "city=Delhi"
```

Response:

```json
{
  "status": "Scanning started"
}
```

Results are available via `/api/results` or WebSocket-like polling.

---

## 🎙️ Voice Commands

EcoLens supports strict voice command recognition. Allowed commands:

| Command | Action |
|---------|--------|
| `scan` | Run Gemini analysis on current frame |
| `save` | Save current scan to history |
| `clear` | Clear results and reset state |
| `history` | View scan history (currently prints status) |
| `quit` / `exit` | Shut down the server |

**How to use:**

1. Click the "Strict Voice Command Simulator" panel in the UI
2. Click the voice buttons to simulate commands, OR
3. Grant microphone permission and speak the commands clearly

The voice listener uses `speech_recognition` with Google's Web Speech API. It gracefully degrades if PyAudio is not installed.

---

## 📂 Project Structure

```
EcoLens-Mini-Project/
├── .env                    # Environment variables (gitignored)
├── .gitignore
├── pyproject.toml          # Project metadata & dependencies
├── uv.lock                 # Lock file for uv
├── README.md               # This file
├── scan_history.json       # Persisted scan history (generated at runtime)
├── saved_scans/            # Directory for scan snapshots
│
├── src/
│   ├── ecolens_mini_project/  # Python package
│   │   ├── __init__.py         # Entry point
│   │   ├── main.py             # Flask app & routes
│   │   ├── ai_engine.py        # Gemini vision engine
│   │   ├── config.py           # Configuration & paths
│   │   └── __main__.py         # Run entry point
│   │
│   └── frontend/               # Static frontend assets
│       ├── index.html          # Main HTML application
│       ├── style.css           # Custom styles
│       └── js/
│           └── app.js          # Frontend JavaScript controller
│
├── .venv/                    # Virtual environment
└── .git/                     # Git repository
```


---

## 🙋‍♂️ Support

- **Issues**: Report bugs or request features via the GitHub Issues tab
- **Contributing**: Pull requests are welcome! Please read the contributing guidelines first
- **Contact**: satyam.vishwakarma@example.com (replace with actual contact)

---

*EcoLens - Turning waste confusion into circular action, one scan at a time.*
