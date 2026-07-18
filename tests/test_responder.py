"""
test_responder.py — Unit tests για το responder module
(Task 5 & 7: έλεγχος ανίχνευσης τύπου, παραγωγής απάντησης και output guardrail)
Τρέξε με: pytest tests/

ΣΗΜΕΙΩΣΗ: όλα τα tests χρησιμοποιούν τον 'mock' provider, οπότε τρέχουν ΧΩΡΙΣ
API key (δωρεάν, offline, σταθερά — ιδανικό για grading/CI).
"""

import sys, os
# Προσθέτουμε το src/ στο path ώστε να βρεθεί το responder package.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from responder.responder import (
    detect_scam_type,
    generate_reply,
    safety_check,
)
from responder.transcript import history_to_markdown


# ── detect_scam_type: σωστή ανίχνευση τύπου ─────────────────────────────────
def test_detect_nigerian_prince():
    # Κείμενο με keywords του nigerian_prince → πρέπει να επιστρέψει αυτόν τον τύπο.
    text = "I am a Prince from Nigeria with an inheritance of million dollars."
    assert detect_scam_type(text) == "nigerian_prince"


def test_detect_lottery():
    text = "Congratulations! You are the winner of our lottery prize, claim now."
    assert detect_scam_type(text) == "lottery"


def test_detect_phishing():
    text = "Security alert: unusual activity. Verify your account and confirm your password."
    assert detect_scam_type(text) == "phishing"


def test_detect_generic_fallback():
    # Κείμενο χωρίς κανένα scam keyword → πρέπει να πέσει στο "generic".
    assert detect_scam_type("Hello, the weather is nice today.") == "generic"


# ── generate_reply (mock): σωστή δομή & συμπεριφορά ─────────────────────────
def test_generate_reply_returns_required_keys():
    # Η απάντηση πρέπει να περιέχει όλα τα αναμενόμενα κλειδιά.
    res = generate_reply("I am a Nigerian prince!", provider="mock")
    for key in ["reply", "scam_type", "turn", "history", "safety"]:
        assert key in res, f"Missing key: {key}"
    assert res["turn"] == 1
    assert isinstance(res["reply"], str) and len(res["reply"]) > 0


def test_generate_reply_does_not_mutate_caller_history():
    # Η αρχική λίστα του caller ΔΕΝ πρέπει να αλλάξει in-place (δουλεύουμε σε copy).
    history = []
    generate_reply("lottery winner, claim your prize!", conversation_history=history,
                   provider="mock")
    assert history == []


def test_scam_type_locks_across_turns():
    # 1ο turn: romance. Το 2ο email αλλάζει θέμα, αλλά ο τύπος πρέπει να ΜΕΙΝΕΙ romance.
    res1 = generate_reply("My beloved, I am lonely and stranded abroad.",
                          provider="mock")
    res2 = generate_reply("Send your bank account number now.",
                          conversation_history=res1["history"], provider="mock")
    assert res1["scam_type"] == "romance"
    assert res2["scam_type"] == "romance"
    assert res2["turn"] == 2


# ── safety_check: το output guardrail δουλεύει ──────────────────────────────
def test_safety_blocks_abuse():
    # Απειλή → safe=False και block.
    res = safety_check("Fine, I will hunt you down and you will pay for this.")
    assert res["safe"] is False
    assert "abusive_content" in res["issues"]


def test_safety_redacts_iban():
    # Πραγματικό-looking IBAN → πρέπει να γίνει redact και να μην εμφανίζεται.
    res = safety_check("Here is my account GB29NWBK60161331926819 for the transfer.")
    assert any(i.startswith("pii_iban") for i in res["issues"])
    assert "GB29NWBK60161331926819" not in res["sanitized_reply"]


def test_safety_redacts_meetup():
    # Κανονισμός πραγματικού ραντεβού → redact + flag (escalation risk).
    res = safety_check("Sure, meet me at the cafe tomorrow at noon.")
    assert "meetup_or_address" in res["issues"]
    assert "[REDACTED" in res["sanitized_reply"]


def test_safety_clean_reply_passes():
    # Καθαρή, αθώα απάντηση → safe=True, καμία επισήμανση.
    res = safety_check("Oh how exciting, please explain the first step again!")
    assert res["safe"] is True
    assert res["issues"] == []


def test_safety_runs_inside_generate_reply():
    # Επιβεβαίωση ότι το guardrail τρέχει ΜΕΣΑ στο generate_reply.
    res = generate_reply("Prince inheritance million dollars", provider="mock")
    assert "safety" in res and isinstance(res["safety"]["issues"], list)


# ── transcript: σωστή παραγωγή markdown ─────────────────────────────────────
def test_transcript_markdown_contains_turns():
    res = generate_reply("Nigerian prince inheritance, transfer funds.",
                         provider="mock")
    md = history_to_markdown(res["history"], scam_type=res["scam_type"])
    assert "Scammer" in md and "Responder" in md
    # Τα εσωτερικά service tags πρέπει να έχουν καθαριστεί από το transcript.
    assert "scam_email" not in md
