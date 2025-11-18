
let mediaRecorder;
let chunks = [];
let currentMode = "command"; // or "enroll"

const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const enrollBtn = document.getElementById("enroll");
const recordBtn = document.getElementById("record");

function setStatus(state, text) {
  let cls = "dot-idle";
  if (state === "listening") cls = "dot-listening";
  if (state === "processing") cls = "dot-processing";
  statusEl.innerHTML = `<span class="dot ${cls}"></span>${text}`;
}

async function initStream() {
  if (mediaRecorder) return;
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (e) => {
    chunks.push(e.data);
  };

  mediaRecorder.onstop = async () => {
    setStatus("processing", "Processing audio with Gemini…");
    const blob = new Blob(chunks, { type: "audio/webm" });
    chunks = [];

    const isEnroll = currentMode === "enroll";
    const url = isEnroll
      ? "/api/enroll-voice?user_id=dhwani"
      : "/api/voice-command?user_id=dhwani";

    const form = new FormData();
    form.append("audio", blob, "audio.webm");

    try {
      const res = await fetch(url, { method: "POST", body: form });
      const json = await res.json();
      logEl.textContent = JSON.stringify(json, null, 2);

      if (res.ok) {
        setStatus(
          "idle",
          isEnroll
            ? "Voice enrolled. Now hold the command button and speak."
            : "Command processed. Ready for the next one."
        );
      } else {
        setStatus("idle", `Error: ${json.message || "Request failed."}`);
      }
    } catch (err) {
      console.error(err);
      setStatus("idle", "Network error sending audio to backend.");
      logEl.textContent = JSON.stringify({ error: String(err) }, null, 2);
    }
  };
}

enrollBtn.addEventListener("click", async () => {
  currentMode = "enroll";
  await initStream();
  chunks = [];
  setStatus("listening", "Listening for enrollment phrase (3 seconds)…");
  mediaRecorder.start();
  setTimeout(() => mediaRecorder.stop(), 3000);
});

// We'll do "tap to record" for simplicity; you can turn this into
// press-and-hold if you want to impress further.
recordBtn.addEventListener("click", async () => {
  currentMode = "command";
  await initStream();
  chunks = [];
  setStatus("listening", "Listening for command (5 seconds)…");
  mediaRecorder.start();
  setTimeout(() => mediaRecorder.stop(), 5000);
});
