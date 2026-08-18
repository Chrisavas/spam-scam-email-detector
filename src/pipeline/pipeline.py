"""
pipeline.py — End-to-end pipeline (classifier -> responder -> multi-turn)
(Task 6: integration of the stages into a single flow + multi-turn behaviour)

WHAT IT DOES:
  Ties the two stages of the system into one flow:
    1. Classifier  -> is the email a scam?
    2. Responder   -> if so, generates a scambaiting reply
    3. Multi-turn  -> keeps conversation history so the conversation continues

  Every session is logged to JSONL for later analysis (without the full history).
"""

import sys
import os
import json
from datetime import datetime

# src/ on the path, so that the classifier & responder packages can be found.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classifier.predict import predict_email
from responder.responder import generate_reply

# Probability threshold above which an email is considered a scam.
SCAM_THRESHOLD = 0.5

# Session log file (git-ignored — it may contain email content).
SESSIONS_FILE = "outputs/sessions.jsonl"


def run_pipeline(email_text: str, session_id: str = None, history: list = None):
    """
    Processes an incoming email through the entire flow.

    Returns a dict with:
      - is_scam     : bool
      - confidence  : float
      - reply       : str or None (if it is not a scam)
      - scam_type   : str
      - history     : updated conversation history (for the next turn)
    """
    # If no session_id is given, we build one from the current time.
    session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    history = history or []

    # ── Step 1: Classification ──
    print(f"\n[1/2] Classifying email...")
    classification = predict_email(email_text)
    # confidence = probability of being a scam -> compared against the threshold.
    is_scam = classification["confidence"] >= SCAM_THRESHOLD

    print(f"      Label     : {classification['label']}")
    print(f"      Confidence: {classification['confidence']:.1%}")

    # Basic skeleton of the result (filled in if it is a scam).
    result = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "email_preview": email_text[:100].replace("\n", " ") + "...",
        "is_scam": is_scam,
        "confidence": classification["confidence"],
        "scam_type": None,
        "reply": None,
        "turn": 0,
        "history": history,
    }

    # If it is NOT a scam -> we generate no reply, we just log it.
    if not is_scam:
        print("      ✓ Legitimate email — no reply generated.")
        _log_session(result)
        return result

    # ── Step 2: Generate Reply (scam only) ──
    print(f"\n[2/2] Generating scambaiting reply...")
    # We pass the history -> the responder keeps continuity (multi-turn) & guardrails.
    response = generate_reply(email_text, history)

    result["scam_type"] = response["scam_type"]
    result["reply"]     = response["reply"]
    result["turn"]      = response["turn"]
    result["history"]   = response["history"]

    print(f"      Scam type : {response['scam_type']}")
    print(f"      Turn #    : {response['turn']}")
    print(f"\n{'─'*60}")
    print(f"  GENERATED REPLY:\n")
    print(f"  {response['reply']}")
    print(f"{'─'*60}")

    _log_session(result)
    return result


def _log_session(result: dict):
    """Logs each session to JSONL (without the full history, for brevity)."""
    os.makedirs("outputs", exist_ok=True)
    log_entry = {k: v for k, v in result.items() if k != "history"}
    with open(SESSIONS_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def multi_turn_demo():
    """
    Demo of the multi-turn behaviour: 3 consecutive scammer messages, where the
    conversation history is carried from turn to turn (same persona throughout).
    """
    print("\n" + "="*60)
    print("  MULTI-TURN SCAMBAITING DEMO")
    print("="*60)

    # 3 scripted scam emails that escalate (asking for details -> asking for money).
    # They are "loaded" with fraud signals (CAPS, !!!, amounts, keywords) so that the
    # classifier consistently flags them as scam and the responder is triggered.
    scam_emails = [
        """Dear Beloved Friend, I am Prince Adebayo, son of the late King of Nigeria.
        I have $45 MILLION DOLLARS in inheritance funds trapped in a bank account!!!
        This is 100% CONFIDENTIAL and URGENT. I need your bank account to transfer
        the money. You will receive 30% commission. Please reply IMMEDIATELY. God bless you!""",

        """CONGRATULATIONS! Thank you for your urgent reply! To proceed with the
        $45 MILLION transfer, please send your FULL NAME, ADDRESS, and BANK ACCOUNT
        NUMBER immediately. We must act NOW before the bank closes the account!!!
        Strictly confidential.""",

        """URGENT!!! To release your $4.5 MILLION inheritance, a processing fee of
        $500 USD is required by the bank. Please send it via WESTERN UNION to our
        barrister in Lagos IMMEDIATELY. Do not delay or the funds will be LOST forever!""",
    ]

    history = []
    session_id = "demo_" + datetime.now().strftime("%H%M%S")

    # We run the pipeline for each email, carrying the history forward each time.
    for i, email in enumerate(scam_emails, 1):
        print(f"\n{'='*60}")
        print(f"  [Scammer Email #{i}]")
        print(f"  {email[:120].strip()}...")
        result = run_pipeline(email, session_id=session_id, history=history)
        history = result["history"]   # -> feeds the next turn

    print(f"\n[✓] Multi-turn demo complete. {len(scam_emails)} turns logged.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ScamAI Pipeline")
    parser.add_argument("--input", type=str, help="Email text to process")
    parser.add_argument("--demo",  action="store_true", help="Run multi-turn demo")
    args = parser.parse_args()

    if args.demo:
        multi_turn_demo()
    elif args.input:
        run_pipeline(args.input)
    else:
        print("Usage: python pipeline.py --input 'email text' OR --demo")
