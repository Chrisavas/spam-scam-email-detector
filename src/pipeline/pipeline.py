"""
pipeline.py — End-to-end pipeline (classifier -> responder -> multi-turn)
(Task 6: ενοποίηση των σταδίων σε ενιαία ροή + multi-turn συμπεριφορά)

ΤΙ ΚΑΝΕΙ:
  Δένει τα δύο στάδια του συστήματος σε μία ροή:
    1. Classifier  -> είναι scam το email;
    2. Responder   -> αν ναι, παράγει scambaiting απάντηση
    3. Multi-turn  -> κρατά conversation history ώστε να συνεχίζει η συνομιλία

  Κάθε session καταγράφεται σε JSONL για μετέπειτα ανάλυση (χωρίς το πλήρες history).
"""

import sys
import os
import json
from datetime import datetime

# Το src/ στο path, ώστε να βρεθούν τα classifier & responder packages.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classifier.predict import predict_email
from responder.responder import generate_reply

# Κατώφλι πιθανότητας πάνω από το οποίο ένα email θεωρείται scam.
SCAM_THRESHOLD = 0.5

# Αρχείο καταγραφής sessions (git-ignored — μπορεί να περιέχει email content).
SESSIONS_FILE = "outputs/sessions.jsonl"


def run_pipeline(email_text: str, session_id: str = None, history: list = None):
    """
    Επεξεργάζεται ένα εισερχόμενο email μέσα από ολόκληρη τη ροή.

    Returns dict με:
      - is_scam     : bool
      - confidence  : float
      - reply       : str ή None (αν δεν είναι scam)
      - scam_type   : str
      - history     : ενημερωμένο conversation history (για το επόμενο turn)
    """
    # Αν δεν δοθεί session_id, φτιάχνουμε ένα από την τρέχουσα ώρα.
    session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    history = history or []

    # ── Βήμα 1: Classification ──
    print(f"\n[1/2] Classifying email...")
    classification = predict_email(email_text)
    # confidence = πιθανότητα να είναι scam -> σύγκριση με το κατώφλι.
    is_scam = classification["confidence"] >= SCAM_THRESHOLD

    print(f"      Label     : {classification['label']}")
    print(f"      Confidence: {classification['confidence']:.1%}")

    # Βασικός σκελετός του αποτελέσματος (συμπληρώνεται αν είναι scam).
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

    # Αν ΔΕΝ είναι scam -> δεν παράγουμε απάντηση, απλώς καταγράφουμε.
    if not is_scam:
        print("      ✓ Legitimate email — no reply generated.")
        _log_session(result)
        return result

    # ── Βήμα 2: Generate Reply (μόνο για scam) ──
    print(f"\n[2/2] Generating scambaiting reply...")
    # Περνάμε το history -> ο responder κρατά συνέχεια (multi-turn) & guardrail.
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
    """Καταγράφει κάθε session σε JSONL (χωρίς το πλήρες history, για συντομία)."""
    os.makedirs("outputs", exist_ok=True)
    log_entry = {k: v for k, v in result.items() if k != "history"}
    with open(SESSIONS_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def multi_turn_demo():
    """
    Demo της multi-turn συμπεριφοράς: 3 διαδοχικά μηνύματα του scammer, όπου το
    conversation history μεταφέρεται από turn σε turn (ίδια persona σε όλα).
    """
    print("\n" + "="*60)
    print("  MULTI-TURN SCAMBAITING DEMO")
    print("="*60)

    # 3 σκηνοθετημένα scam emails που κλιμακώνουν (ζητούν στοιχεία -> ζητούν χρήματα).
    # Είναι "γεμάτα" σήματα απάτης (CAPS, !!!, ποσά, keywords) ώστε ο classifier
    # να τα εντοπίζει σταθερά ως scam και να ενεργοποιείται ο responder.
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

    # Τρέχουμε το pipeline για κάθε email, μεταφέροντας το history κάθε φορά.
    for i, email in enumerate(scam_emails, 1):
        print(f"\n{'='*60}")
        print(f"  [Scammer Email #{i}]")
        print(f"  {email[:120].strip()}...")
        result = run_pipeline(email, session_id=session_id, history=history)
        history = result["history"]   # -> τροφοδοτεί το επόμενο turn

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
