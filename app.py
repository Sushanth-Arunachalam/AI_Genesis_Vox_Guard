
import os
import json
import pathlib
from urllib.parse import urlencode, quote_plus

from flask import Flask, render_template, request, jsonify

from google import genai
from google.genai import types

# --- Setup ---

app = Flask(__name__)

# Directory to store enrolled voice samples
VOICEPRINT_DIR = pathlib.Path("voiceprints")
VOICEPRINT_DIR.mkdir(exist_ok=True)

# Gemini client: expects GOOGLE_API_KEY in environment
client = genai.Client(api_key="AIzaSyB_t1uX-_BuCAm3u6MfghDEDXTaPB60BEU")
MODEL = "gemini-2.5-flash"  # change if your hackathon specifies a different model

# In-memory todo storage for demo
TODOS = []


# --- Tool (function) definitions for Gemini ---

send_email_fn = {
    "name": "send_email",
    "description": "Send an email on behalf of the user.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string"},
            "body": {"type": "string"},
        },
        "required": ["to", "subject", "body"],
    },
}

add_todo_fn = {
    "name": "add_todo",
    "description": "Add a new task to the user's to-do list.",
    "parameters": {
        "type": "object",
        "properties": {
            "task": {"type": "string"},
            "due_date": {
                "type": "string",
                "description": "Optional due date, e.g. 'today evening' or '2025-11-18'",
            },
        },
        "required": ["task"],
    },
}

request_uber_fn = {
    "name": "request_uber_ride",
    "description": "Prepare a deep link URL to request an Uber ride.",
    "parameters": {
        "type": "object",
        "properties": {
            "pickup": {"type": "string", "description": "Pickup location description"},
            "dropoff": {"type": "string", "description": "Dropoff location description"},
        },
        "required": ["pickup", "dropoff"],
    },
}

tools = types.Tool(function_declarations=[send_email_fn, add_todo_fn, request_uber_fn])
config = types.GenerateContentConfig(tools=[tools])


# --- Helper: extract text from a Gemini response (for JSON parsing, etc.) ---

def extract_text(response):
    #"\"\"Concatenate all text parts from a Gemini response into a single string.\"\"\"
    texts = []
    for cand in getattr(response, "candidates", []):
        content = getattr(cand, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []):
            if getattr(part, "text", None):
                texts.append(part.text)
    return "\n".join(texts).strip()


# --- Voice biometric functions ---

def verify_voice(user_id: str, audio_bytes: bytes, threshold: float = 0.7) -> bool:
    #\"\"\"
    #Simple voice verification using Gemini as a speaker-verification helper.
    #Compares the enrolled voice sample for user_id with the new audio_bytes.
    #\"\"\"
    enrolled_path = VOICEPRINT_DIR / f"{user_id}.webm"
    if not enrolled_path.exists():
        # No enrollment yet, treat as not verified
        return False

    with open(enrolled_path, "rb") as f:
        enrolled_bytes = f.read()

    prompt = (
        "You are a speaker verification system. "
        "You will receive two audio clips: enrolled voice, then live voice. "
        "Return ONLY a JSON object with fields "
        "`same_speaker` (true/false) and `similarity` (number between 0 and 1)."
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part(text=prompt),
            types.Part.from_bytes(data=enrolled_bytes, mime_type="audio/webm"),
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm"),
        ],
    )

    text = extract_text(response)
    try:
        result = json.loads(text)
        similarity = float(result.get("similarity", 0.0))
        same_speaker = bool(result.get("same_speaker"))
        return same_speaker and similarity >= threshold
    except Exception:
        # If parsing fails, be safe and deny
        return False


# --- Gemini function-calling for intent + tool selection ---

def gemini_understand_audio_and_pick_action(audio_bytes: bytes, user_id: str):
    '''\"\"\"
    Send audio to Gemini, ask it to understand the spoken command and pick
    which tool to call (send_email, add_todo, request_uber_ride).
    Returns the function_call object or None.
    \"\"\"'''
    system_prompt = (
        "You are a voice assistant for a single authenticated user. "
        "First, understand the user's spoken command from the audio. "
        "Then, if appropriate, call one of the available tools: "
        "send_email, add_todo, or request_uber_ride. "
        "Infer reasonable email subjects/bodies and ride locations if needed. "
        "If the user is just chatting and no tool is needed, do not call any tool."
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(text=system_prompt),
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/webm",  # matches the browser recording format
                ),
            ],
        )
    ]

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )

    # Look for a function_call in the first candidate's parts
    if not response.candidates:
        return None

    candidate = response.candidates[0]
    content = candidate.content
    for part in content.parts:
        fc = getattr(part, "function_call", None)
        if fc:
            return fc

    return None


# --- Tool implementations (backend logic) ---

def send_email(to: str, subject: str, body: str) -> str:
    '''\"\"\"
    For the hackathon demo, we just log the email on the server.
    You can replace this with an actual email service if allowed.
    \"\"\"'''
    print(f"[MOCK EMAIL] To: {to} | Subject: {subject}\n{body}\n")
    return f"Email sent to {to} with subject '{subject}'."


def add_todo(task: str, due_date: str | None = None) -> str:
    TODOS.append({"task": task, "due_date": due_date})
    if due_date:
        return f"Added task: '{task}' (due {due_date})."
    return f"Added task: '{task}'."


def request_uber_ride(pickup: str, dropoff: str) -> str:
    '''\"\"\"
    For demo purposes, construct an Uber deep-link that can be opened on mobile.
    Pickup is set to 'my_location'; dropoff uses the address text.
    \"\"\"'''
    base = "https://m.uber.com/ul/"
    params = {
        "action": "setPickup",
        "pickup": "my_location",
        "dropoff[formatted_address]": dropoff,
    }
    url = base + "?" + urlencode(params, quote_via=quote_plus)
    return f"Uber deep link prepared: {url}"


# --- Flask routes ---

@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/enroll-voice")
def enroll_voice():
    user_id = request.args.get("user_id", "default_user")
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"status": "error", "message": "No audio file provided."}), 400

    audio_bytes = audio_file.read()

    filepath = VOICEPRINT_DIR / f"{user_id}.webm"
    with open(filepath, "wb") as f:
        f.write(audio_bytes)

    return jsonify({"status": "ok", "message": f"Voice enrolled for {user_id}."})


@app.post("/api/voice-command")
def voice_command():
    user_id = request.args.get("user_id", "default_user")
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"status": "error", "message": 'No audio file provided.'}), 400

    audio_bytes = audio_file.read()

    # 1) Biometric auth
    #if not verify_voice(user_id, audio_bytes):
        #return jsonify({"status": "error", "message": "Voice authentication failed."}), 401

    # 2) Let Gemini decide which tool to call
    tool_call = gemini_understand_audio_and_pick_action(audio_bytes, user_id)
    '''if tool_call is None:
        tool_call= send_email
        return jsonify({
            "status": "ok",
            "called_tool": "send_email",
            "message": "I understood your command, but no actionable tool was needed."
        })'''

    name = send_email

    # Convert args to a plain dict (depending on client version, this may already be a dict)
    args = dict(tool_call.args or {})

    # 3) Execute actual functions
    if name == "send_email":
        result_msg = send_email(**args)
    elif name == "add_todo":
        result_msg = add_todo(**args)
    elif name == "request_uber_ride":
        result_msg = request_uber_ride(**args)
    else:
        result_msg = f"Unknown tool: {name}"

    return jsonify({
        "status": "ok",
        "called_tool": name,
        "args": args,
        "message": result_msg,
    })


if __name__ == "__main__":
    # For local development
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
