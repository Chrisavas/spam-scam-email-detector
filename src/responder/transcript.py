"""
transcript.py — Multi-turn Transcript Exporter
(υποστηρίζει Task 6 demo & Task 8 report: export συνομιλιών σε markdown)

ΤΙ ΚΑΝΕΙ:
  Παίρνει το conversation_history που γυρίζει ο responder.generate_reply() και το
  γράφει σε καθαρό markdown, έτοιμο να μπει ως παράδειγμα στο report ή στα slides.

ΧΡΗΣΗ:
    from responder.responder import generate_reply
    from responder.transcript import export_markdown

    history = []
    for email in scam_emails:
        res = generate_reply(email, conversation_history=history, provider="mock")
        history = res["history"]
    export_markdown(history, "outputs/transcript_nigerian.md",
                    scam_type=res["scam_type"])
"""

import os
import re
from datetime import datetime


def _strip_tags(content: str) -> str:
    """
    Καθαρίζει τα εσωτερικά service markers/tags ώστε το transcript να διαβάζεται
    ωραία (αφαιρεί το '[Scam email received]:' και τα <scam_email> tags).
    """
    content = content.replace("[Scam email received]:", "").strip()
    content = re.sub(r"</?scam_email>", "", content).strip()
    return content


def history_to_markdown(history: list, scam_type: str = "unknown",
                        title: str = "Scambaiting Transcript") -> str:
    """Μετατρέπει το conversation_history σε markdown string (χωρίς να γράφει αρχείο)."""
    # Επικεφαλίδα + metadata (τύπος, ημερομηνία, πλήθος turns).
    lines = [
        f"# {title}",
        "",
        f"- **Scam type:** `{scam_type}`",
        f"- **Generated:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **Turns (our replies):** "
        f"{len([m for m in history if m.get('role') == 'assistant'])}",
        "",
        # Disclaimer — σημαντικό για το academic/ethics πλαίσιο.
        "> ⚠️ Academic scambaiting demo. All targets/content are simulated; "
        "no real personal data, money, or contact details are exchanged.",
        "",
        "---",
        "",
    ]

    # Διατρέχουμε το history και τυπώνουμε εναλλάξ scammer / δική μας απάντηση.
    turn = 0
    for msg in history:
        role = msg.get("role")
        body = _strip_tags(msg.get("content", ""))
        if role == "user":          # μήνυμα του scammer
            turn += 1
            lines += [f"### 🎯 Scammer — message {turn}", "", "```", body, "```", ""]
        elif role == "assistant":   # δική μας (ασφαλής) απάντηση
            lines += [f"### 🤖 Responder (our reply)", "", body, "", "---", ""]

    return "\n".join(lines)


def export_markdown(history: list, path: str, scam_type: str = "unknown",
                    title: str = "Scambaiting Transcript") -> str:
    """Γράφει το transcript σε αρχείο markdown και επιστρέφει το path."""
    # Δημιουργούμε τον φάκελο προορισμού αν δεν υπάρχει.
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    md = history_to_markdown(history, scam_type=scam_type, title=title)
    # encoding="utf-8" για να γράφονται σωστά ελληνικά/emoji.
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[✓] Transcript saved: {path}")
    return path


if __name__ == "__main__":
    # Mini self-demo: παράγει ένα 3-turn transcript offline (mock provider).
    import sys
    # Προσθέτουμε το src/ στο path ώστε να βρεθεί το responder package.
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from responder.responder import generate_reply   # όταν τρέχει ως package
    except ModuleNotFoundError:
        from responder import generate_reply              # όταν τρέχει ως σκέτο script

    emails = [
        "Dear Friend, I am Prince Adebayo from Nigeria with $15 million dollars "
        "to transfer. I will give you 30%. Reply urgently!",
        "Thank you! Please send your full name and bank account number to proceed.",
        "We need a $500 processing fee via Western Union to release the funds.",
    ]
    history, res = [], None
    for e in emails:
        res = generate_reply(e, conversation_history=history, provider="mock")
        history = res["history"]

    export_markdown(history, "outputs/transcript_demo.md",
                    scam_type=res["scam_type"])
