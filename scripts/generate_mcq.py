import json
import os
import sys
import time
from pathlib import Path

from groq import Groq

# ============================
# CONFIG
# ============================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

CURRENT_TOPIC_FILE = Path("current_topic.json")
TRANSCRIPT_FILE = Path("script.txt")

# MCQ REPO OUTPUT
MCQ_REPO_ROOT = Path("../open-university-mcq")
MCQ_OUTPUT_DIR = MCQ_REPO_ROOT / "tests"

PAYPAL_ID_FILE = MCQ_REPO_ROOT / "PAYPAL_ID.txt"

MCQ_LINK_FILE = Path("mcq_link.txt")

REQUIRED_QUESTIONS = 10

MAX_RETRIES = 2
BACKOFF_SECONDS = 2


# ============================
# GROQ (RATE-LIMIT SAFE)
# ============================

def groq_generate(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")

    client = Groq(api_key=GROQ_API_KEY)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an academic examiner. "
                            "You MUST return STRICT JSON only. "
                            "No markdown. No prose. No commentary."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.25,
                max_tokens=1800,
            )
            return resp.choices[0].message.content.strip()

        except Exception as e:
            if attempt >= MAX_RETRIES:
                raise
            time.sleep(BACKOFF_SECONDS * attempt)


# ============================
# HTML (UNCHANGED)
# ============================

def generate_html(topic_id, title, questions, paypal_id):
    q_json = json.dumps(questions)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title} – Practice Test</title>

<style>
:root {{
  --blue: #1e3a8a;
  --red-bg: #fee2e2;
  --red-text: #991b1b;
  --green: #16a34a;
  --red: #dc2626;
}}

body {{
  margin: 0;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  background: #f9fafb;
  color: #0f172a;
}}

/* HEADER */
header {{
  background: var(--blue);
  color: white;
  padding: 18px 22px;
  font-size: 24px;
}}

/* DONATION BANNER (Wikipedia style) */
#donationBanner {{
  background: var(--red-bg);
  color: var(--red-text);
  padding: 14px 18px;
  font-weight: 600;
  cursor: pointer;
}}

/* CONTENT */
.container {{
  padding: 22px;
}}

.question {{
  margin-bottom: 22px;
}}

.options label {{
  display: block;
  margin: 6px 0;
  cursor: pointer;
}}

/* BUTTONS */
button {{
  padding: 10px 18px;
  font-size: 15px;
  cursor: pointer;
  border-radius: 6px;
  border: none;
}}

.btn-green {{
  background: var(--green);
  color: white;
}}

.btn-red {{
  background: var(--red);
  color: white;
}}

/* MODAL */
.modal-overlay {{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}}

.modal {{
  background: white;
  width: 92%;
  max-width: 520px;
  border-radius: 10px;
  padding: 22px;
}}

.modal h2 {{
  margin-top: 0;
}}

.modal small {{
  color: #475569;
}}

.payment-box {{
  margin: 14px 0;
}}

/* HIDE */
.hidden {{
  display: none;
}}
</style>
</head>

<body>

<!-- MODAL -->
<div id="donationModal" class="modal-overlay">
  <div class="modal">
    <h2>Please Donate for our Hardwork</h2>
    <small>Right contribution shows your respect for lesson / dedication</small>

    <p><b>Select payment method:</b></p>

    <button onclick="showGpay()">GPay</button>
    <button onclick="showPaypal()">PayPal</button>

    <div id="paymentBox" class="payment-box"></div>

    <br/><br/>
    <button class="btn-green" onclick="confirmPaid()">I Paid</button>
    <button class="btn-red" onclick="closeModal()">Cancel</button>
  </div>
</div>

<header>{title}</header>

<div id="donationBanner" onclick="openModal()">
  Please consider donating before attempting this test.
</div>

<div class="container">
  <div id="quiz"></div>

  <button onclick="submitQuiz()">Submit</button>
  <p id="result"></p>
</div>

<script>
const QUESTIONS = {q_json};

function openModal() {{
  document.getElementById("donationModal").classList.remove("hidden");
}}

function closeModal() {{
  alert("We have put so much of effort.\\n Is this right not show the minimum respect to our work ? \\n You think and re-consider.");
  document.getElementById("donationModal").classList.add("hidden");
  document.getElementById("donationBanner").style.display = "block";
}}

function confirmPaid() {{
  document.getElementById("donationModal").classList.add("hidden");
  document.getElementById("donationBanner").style.display = "none";
}}

function showGpay() {{
  document.getElementById("paymentBox").innerHTML =
    '<p>Scan QR:</p><img src="../payment/gpay/qr.png" width="220"/>';
}}

function showPaypal() {{
  document.getElementById("paymentBox").innerHTML =
    '<p>PayPal ID: <b>{paypal_id}</b></p>';
}}

/* QUIZ */
function renderQuiz() {{
  let html = "";
  QUESTIONS.forEach((q, i) => {{
    html += `<div class="question"><b>${{{{i+1}}}}. ${{{{q.q}}}}</b><div class="options">`;
    q.options.forEach((o, j) => {{
      html += `<label><input type="radio" name="q${{{{i}}}}" value="${{{{j}}}}"/> ${{{{o}}}}</label>`;
    }});
    html += "</div></div>";
  }});
  document.getElementById("quiz").innerHTML = html;
}}

function submitQuiz() {{
  let score = 0;
  QUESTIONS.forEach((q, i) => {{
    const sel = document.querySelector(`input[name="q${{{{i}}}}"]:checked`);
    if (sel && Number(sel.value) === q.answer) score++;
  }});
  document.getElementById("result").innerText =
    `Score: ${{{{score}}}} / ${{{{QUESTIONS.length}}}}`;
}}

/* INIT */
renderQuiz();
openModal();
</script>

</body>
</html>
"""


# ============================
# MAIN
# ============================

def main():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY missing")
        sys.exit(1)

    if not CURRENT_TOPIC_FILE.exists():
        print("ERROR: current_topic.json missing")
        sys.exit(1)

    if not TRANSCRIPT_FILE.exists():
        print("ERROR: script.txt missing")
        sys.exit(1)

    if not MCQ_REPO_ROOT.exists():
        print("ERROR: open-university-mcq repo not found")
        sys.exit(1)

    if not PAYPAL_ID_FILE.exists():
        print("ERROR: PAYPAL_ID.txt missing in MCQ repo")
        sys.exit(1)

    topic = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
    transcript = TRANSCRIPT_FILE.read_text(encoding="utf-8").strip()

    prompt = f"""
Generate EXACTLY {REQUIRED_QUESTIONS} exam-style MCQs.

Rules:
- Use ONLY the transcript
- Output VALID JSON ONLY
- No markdown
- No commentary

Schema:
{{
  "questions": [
    {{
      "q": "",
      "options": ["", "", "", ""],
      "answer": 0,
      "explanation": ""
    }}
  ]
}}

Transcript:
<<<
{transcript}
>>>
"""

    raw = groq_generate(prompt)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("ERROR: LLM did not return valid JSON")
        print(raw[:800])
        sys.exit(1)

    questions = data.get("questions", [])
    if len(questions) != REQUIRED_QUESTIONS:
        print("ERROR: wrong number of questions")
        sys.exit(1)

    MCQ_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paypal_id = PAYPAL_ID_FILE.read_text().strip()

    html = generate_html(
        topic_id=topic["id"],
        title=topic["title"],
        questions=questions,
        paypal_id=paypal_id,
    )

    out_file = MCQ_OUTPUT_DIR / f"{topic['id']}.html"
    out_file.write_text(html, encoding="utf-8")

    mcq_url = f"https://surajit93.github.io/open-university-mcq/tests/{topic['id']}.html"
    MCQ_LINK_FILE.write_text(mcq_url, encoding="utf-8")

    print("✔ MCQ published:", mcq_url)


if __name__ == "__main__":
    main()
