"""
test_preprocessing.py — Unit tests for the preprocessing module
(Task 2: verifying the correctness of text cleaning and feature extraction)

WHAT IT CHECKS:
  Confirms that the two core preprocessing functions work correctly:
    • clean_text()      — removes HTML/URLs, converts to lowercase
    • extract_features()— produces the 8 numeric features (+ cleaned_text)

  These features feed directly into the classifier (Task 4), so an error here
  would silently "poison" the whole model. That is why the tests cover both a
  typical scam and a typical legit email.

Run with: pytest tests/
"""

import sys, os
# Add the project root to the path so that the src package can be found.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.preprocessing.preprocess import clean_text, extract_features


# ── clean_text: text cleaning ───────────────────────────────────────────────
def test_clean_text_removes_html():
    # HTML tags must be removed, the content must remain (lowercased).
    result = clean_text("<b>Hello</b> World")
    assert "<b>" not in result
    assert "hello" in result


def test_clean_text_removes_urls():
    # URLs are removed (a common hiding place for phishing links).
    result = clean_text("Visit http://scam.com for details")
    assert "http" not in result


def test_clean_text_lowercases():
    # Uniformity: everything lowercase, so that "URGENT" and "urgent" count the same.
    result = clean_text("HELLO WORLD")
    assert result == "hello world"


# ── extract_features: feature extraction ────────────────────────────────────
def test_extract_features_scam_keywords():
    # Typical scam: the fraud signals must "light up" — scam keywords, money
    # mentions, exclamation marks and uppercase ratio.
    scam_text = "URGENT! I am a Nigerian Prince with $15 million dollars. 100% confidential!!!"
    features = extract_features(scam_text)
    assert features["scam_keyword_count"] > 0
    assert features["money_mentions"] > 0
    assert features["exclamation_count"] >= 2
    assert features["caps_ratio"] > 0


def test_extract_features_legit_email():
    # Typical legit: no fraud signals (0 scam keywords, 0 money mentions).
    # Confirms that we do not get excessive false positives at the feature level.
    legit_text = "Hi John, see you at the office tomorrow at 3pm. Thanks for lunch yesterday! Sarah."
    features = extract_features(legit_text)
    assert features["scam_keyword_count"] == 0
    assert features["money_mentions"] == 0


def test_extract_features_returns_all_keys():
    # Module contract: all 9 fields must ALWAYS be returned
    # (8 numeric features + cleaned_text). If one is missing, the classifier breaks.
    features = extract_features("test email")
    expected_keys = [
        "word_count", "unique_words", "avg_word_length",
        "scam_keyword_count", "caps_ratio",
        "exclamation_count", "question_count", "money_mentions",
        "cleaned_text",
    ]
    for key in expected_keys:
        assert key in features, f"Missing feature: {key}"
