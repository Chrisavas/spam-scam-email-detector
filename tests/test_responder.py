"""
test_responder.py — Unit tests for the responder module
(Tasks 5 & 7: checking type detection, reply generation and the output guardrail)
Run with: pytest tests/

NOTE: all tests use the 'mock' provider, so they run WITHOUT an API key
(free, offline, deterministic — ideal for grading/CI).
"""

import sys, os
# Add src/ to the path so that the responder package can be found.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from responder.responder import (
    detect_scam_type,
    generate_reply,
    safety_check,
)
from responder.transcript import history_to_markdown


# ── detect_scam_type: correct type detection ────────────────────────────────
def test_detect_nigerian_prince():
    # Text with nigerian_prince keywords → must return that type.
    text = "I am a Prince from Nigeria with an inheritance of million dollars."
    assert detect_scam_type(text) == "nigerian_prince"


def test_detect_lottery():
    text = "Congratulations! You are the winner of our lottery prize, claim now."
    assert detect_scam_type(text) == "lottery"


def test_detect_phishing():
    text = "Security alert: unusual activity. Verify your account and confirm your password."
    assert detect_scam_type(text) == "phishing"


def test_detect_generic_fallback():
    # Text with no scam keyword at all → must fall back to "generic".
    assert detect_scam_type("Hello, the weather is nice today.") == "generic"


# ── generate_reply (mock): correct structure & behaviour ────────────────────
def test_generate_reply_returns_required_keys():
    # The response must contain all the expected keys.
    res = generate_reply("I am a Nigerian prince!", provider="mock")
    for key in ["reply", "scam_type", "turn", "history", "safety"]:
        assert key in res, f"Missing key: {key}"
    assert res["turn"] == 1
    assert isinstance(res["reply"], str) and len(res["reply"]) > 0


def test_generate_reply_does_not_mutate_caller_history():
    # The caller's original list must NOT be modified in place (we work on a copy).
    history = []
    generate_reply("lottery winner, claim your prize!", conversation_history=history,
                   provider="mock")
    assert history == []


def test_scam_type_locks_across_turns():
    # 1st turn: romance. The 2nd email changes topic, but the type must STAY romance.
    res1 = generate_reply("My beloved, I am lonely and stranded abroad.",
                          provider="mock")
    res2 = generate_reply("Send your bank account number now.",
                          conversation_history=res1["history"], provider="mock")
    assert res1["scam_type"] == "romance"
    assert res2["scam_type"] == "romance"
    assert res2["turn"] == 2


# ── safety_check: the output guardrail works ────────────────────────────────
def test_safety_blocks_abuse():
    # Threat → safe=False and blocked.
    res = safety_check("Fine, I will hunt you down and you will pay for this.")
    assert res["safe"] is False
    assert "abusive_content" in res["issues"]


def test_safety_redacts_iban():
    # A real-looking IBAN → must be redacted and must not appear.
    res = safety_check("Here is my account GB29NWBK60161331926819 for the transfer.")
    assert any(i.startswith("pii_iban") for i in res["issues"])
    assert "GB29NWBK60161331926819" not in res["sanitized_reply"]


def test_safety_redacts_meetup():
    # Arranging a real meeting → redact + flag (escalation risk).
    res = safety_check("Sure, meet me at the cafe tomorrow at noon.")
    assert "meetup_or_address" in res["issues"]
    assert "[REDACTED" in res["sanitized_reply"]


def test_safety_clean_reply_passes():
    # A clean, harmless reply → safe=True, no flags.
    res = safety_check("Oh how exciting, please explain the first step again!")
    assert res["safe"] is True
    assert res["issues"] == []


def test_safety_runs_inside_generate_reply():
    # Confirmation that the guardrail runs INSIDE generate_reply.
    res = generate_reply("Prince inheritance million dollars", provider="mock")
    assert "safety" in res and isinstance(res["safety"]["issues"], list)


# ── transcript: correct markdown generation ─────────────────────────────────
def test_transcript_markdown_contains_turns():
    res = generate_reply("Nigerian prince inheritance, transfer funds.",
                         provider="mock")
    md = history_to_markdown(res["history"], scam_type=res["scam_type"])
    assert "Scammer" in md and "Responder" in md
    # The internal service tags must have been stripped from the transcript.
    assert "scam_email" not in md
