"""
pipeline.py — End-to-End Pipeline
Αρμόδιο άτομο: Άτομο 4

Συνδέει:
  1. Classifier  → Είναι scam;
  2. Responder   → Παράγει απάντηση
  3. Multi-turn  → Συνεχίζει τη συνομιλία
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classifier.predict import predict_email
from responder.responder import generate_reply

# Threshold πάνω από το οποίο θεωρούμε scam
SCAM_THRESHOLD = 0.5

# Αποθήκευση sessions
SESSIONS_FILE = "outputs/sessions.jsonl"


def run_pipeline(email_text: str, session_id: str = None, history: list = None):
    """
    Επεξεργάζεται ένα εισερχόμενο email.

    Returns dict με:
      - is_scam     : bool
      - confidence  : float
      - reply       : str ή None (αν δεν είναι scam)
      - scam_type   : str
      - history     : updated conversation history
    """
    session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    history = history or []

    # ── Βήμα 1: Classification ──
    print(f"\n[1/2] Classifying email...")
    classification = predict_email(email_text)
    is_scam = classification["confidence"] >= SCAM_THRESHOLD

    print(f"      Label     : {classification['label']}")
    print(f"      Confidence: {classification['confidence']:.1%}")

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

    if not is_scam:
        print("      ✓ Legitimate email — no reply generated.")
        _log_session(result)
        return result

    # ── Βήμα 2: Generate Reply ──
    print(f"\n[2/2] Generating scambaiting reply...")
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
    """Αποθηκεύει κάθε session σε JSONL για ανάλυση."""
    os.makedirs("outputs", exist_ok=True)
    log_entry = {k: v for k, v in result.items() if k != "history"}
    with open(SESSIONS_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def multi_turn_demo():
    """Δείχνει multi-turn συνομιλία με τον scammer."""
    print("\n" + "="*60)
    print("  MULTI-TURN SCAMBAITING DEMO")
    print("="*60)

    scam_emails = [
        """Dear Beloved Friend, I am Prince Adebayo from Nigeria.
        I have $15 million dollars to transfer and need your help.
        You will receive 30% commission. Reply urgently!""",

        """Thank you for your interest! Please send your full name,
        address, and bank account number so we can proceed with
        the transfer immediately.""",

        """We need $500 processing fee to release your $4.5 million.
        Please send via Western Union to Lagos immediately!""",
    ]

    history = []
    session_id = "demo_" + datetime.now().strftime("%H%M%S")

    for i, email in enumerate(scam_emails, 1):
        print(f"\n{'='*60}")
        print(f"  [Scammer Email #{i}]")
        print(f"  {email[:120].strip()}...")
        result = run_pipeline(email, session_id=session_id, history=history)
        history = result["history"]

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
