"""
test_preprocessing.py — Unit tests για το preprocessing module
Τρέξε με: pytest tests/
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.preprocessing.preprocess import clean_text, extract_features


def test_clean_text_removes_html():
    result = clean_text("<b>Hello</b> World")
    assert "<b>" not in result
    assert "hello" in result


def test_clean_text_removes_urls():
    result = clean_text("Visit http://scam.com for details")
    assert "http" not in result


def test_clean_text_lowercases():
    result = clean_text("HELLO WORLD")
    assert result == "hello world"


def test_extract_features_scam_keywords():
    scam_text = "URGENT! I am a Nigerian Prince with $15 million dollars. 100% confidential!!!"
    features = extract_features(scam_text)
    assert features["scam_keyword_count"] > 0
    assert features["money_mentions"] > 0
    assert features["exclamation_count"] >= 2
    assert features["caps_ratio"] > 0


def test_extract_features_legit_email():
    legit_text = "Hi John, just confirming our meeting tomorrow at 3pm. Best regards, Sarah."
    features = extract_features(legit_text)
    assert features["scam_keyword_count"] == 0
    assert features["money_mentions"] == 0


def test_extract_features_returns_all_keys():
    features = extract_features("test email")
    expected_keys = [
        "word_count", "unique_words", "avg_word_length",
        "scam_keyword_count", "caps_ratio",
        "exclamation_count", "question_count", "money_mentions",
        "cleaned_text",
    ]
    for key in expected_keys:
        assert key in features, f"Missing feature: {key}"
