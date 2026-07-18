"""
test_preprocessing.py — Unit tests για το preprocessing module
(Task 2: έλεγχος ορθότητας του καθαρισμού κειμένου και της εξαγωγής χαρακτηριστικών)

ΤΙ ΕΛΕΓΧΕΙ:
  Επιβεβαιώνει ότι οι δύο βασικές συναρτήσεις του preprocessing δουλεύουν σωστά:
    • clean_text()      — αφαιρεί HTML/URLs, μετατρέπει σε πεζά
    • extract_features()— παράγει τα 8 αριθμητικά features (+ cleaned_text)

  Τα features αυτά τροφοδοτούν απευθείας τον classifier (Task 4), οπότε ένα σφάλμα
  εδώ θα «μόλυνε» σιωπηλά όλο το μοντέλο. Γι' αυτό τα tests καλύπτουν τόσο ένα
  τυπικό scam όσο και ένα τυπικό legit email.

Τρέξε με: pytest tests/
"""

import sys, os
# Προσθέτουμε τη ρίζα του project στο path ώστε να βρεθεί το πακέτο src.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.preprocessing.preprocess import clean_text, extract_features


# ── clean_text: καθαρισμός κειμένου ─────────────────────────────────────────
def test_clean_text_removes_html():
    # Τα HTML tags πρέπει να αφαιρούνται, το περιεχόμενο να μένει (πεζό).
    result = clean_text("<b>Hello</b> World")
    assert "<b>" not in result
    assert "hello" in result


def test_clean_text_removes_urls():
    # Τα URLs αφαιρούνται (συχνό σημείο απόκρυψης phishing links).
    result = clean_text("Visit http://scam.com for details")
    assert "http" not in result


def test_clean_text_lowercases():
    # Ομοιομορφία: όλα πεζά, ώστε "URGENT" και "urgent" να μετρούν το ίδιο.
    result = clean_text("HELLO WORLD")
    assert result == "hello world"


# ── extract_features: εξαγωγή χαρακτηριστικών ───────────────────────────────
def test_extract_features_scam_keywords():
    # Τυπικό scam: πρέπει να «ανάβουν» τα σήματα απάτης — scam keywords, αναφορές
    # χρημάτων, θαυμαστικά και ποσοστό κεφαλαίων.
    scam_text = "URGENT! I am a Nigerian Prince with $15 million dollars. 100% confidential!!!"
    features = extract_features(scam_text)
    assert features["scam_keyword_count"] > 0
    assert features["money_mentions"] > 0
    assert features["exclamation_count"] >= 2
    assert features["caps_ratio"] > 0


def test_extract_features_legit_email():
    # Τυπικό legit: κανένα σήμα απάτης (0 scam keywords, 0 αναφορές χρημάτων).
    # Επιβεβαιώνει ότι δεν έχουμε υπερβολικά false positives στο feature level.
    legit_text = "Hi John, see you at the office tomorrow at 3pm. Thanks for lunch yesterday! Sarah."
    features = extract_features(legit_text)
    assert features["scam_keyword_count"] == 0
    assert features["money_mentions"] == 0


def test_extract_features_returns_all_keys():
    # Συμβόλαιο (contract) του module: πρέπει ΠΑΝΤΑ να επιστρέφονται και τα 9 πεδία
    # (8 αριθμητικά features + cleaned_text). Αν κάποιο λείψει, ο classifier σπάει.
    features = extract_features("test email")
    expected_keys = [
        "word_count", "unique_words", "avg_word_length",
        "scam_keyword_count", "caps_ratio",
        "exclamation_count", "question_count", "money_mentions",
        "cleaned_text",
    ]
    for key in expected_keys:
        assert key in features, f"Missing feature: {key}"
