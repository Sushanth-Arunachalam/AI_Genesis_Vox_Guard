
# AI Voice Agent – Gemini + Audio Biometrics (Flask Demo)

This is a ready-to-run Flask project for a hackathon-style **voice-only AI agent**:

- Uses **Gemini** (via `google-genai`) for:
  - Audio understanding (speech → intent)
  - Tool (function) calling to decide actions
  - Simple speaker verification (compare enrolled vs live voice)
- Uses **Flask** for the backend and a simple HTML/JS frontend.
- Supports:
  - **Voice enrollment** (register your voice)
  - **Authenticated voice commands** (send mock email, add todo, generate Uber deep link)

## Project structure

```bash
voice_agent_flask/
├─ app.py
├─ requirements.txt
├─ README.md
├─ templates/
│  └─ index.html
├─ static/
│  └─ script.js
└─ voiceprints/        # created at runtime for enrolled voices
```

## Setup

1. **Create and activate a virtual environment (optional but recommended)**

```bash
cd voice_agent_flask
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set your Gemini API key**

You must have a valid Gemini API key from Google AI Studio.

```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"   # PowerShell: $env:GOOGLE_API_KEY="..."
```

4. **Run the Flask app**

```bash
python app.py
```

The app will start at `http://localhost:5000`.

## How to demo

1. Open `http://localhost:5000` in Chrome.
2. Click **“Enroll my voice”** and speak a short phrase when prompted.
3. After enrollment succeeds, click **“Hold to speak command”** and say commands like:
   - “Send an email to my professor confirming I will proctor the exam at 3:10 pm.”
   - “Add a todo to book my Uber for tomorrow morning.”
   - “Book me an Uber from home to Yeshiva University.”

If voice similarity is high enough, the backend:

- Verifies your voice (biometric step).
- Asks Gemini to understand the audio and select the right tool.
- Executes the mocked `send_email`, `add_todo`, or `request_uber_ride` function.
- Returns a JSON response with what happened (shown in the UI log box).

This is intentionally structured to be **easy to extend**:
- Add new capabilities by defining a new function and putting its JSON schema into the `tools` list.
