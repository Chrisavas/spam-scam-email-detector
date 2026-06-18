"""
predict.py — Spam/Scam Prediction
Αρμόδιο άτομο: Άτομο 2

Φορτώνει το trained model και κάνει prediction
για νέα emails.
"""

import pickle
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from preprocessing.preprocess import extract_features
import pandas as pd


def load_model(model_path: str = "outputs/classifier.pkl"):
    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
    return bundle["model"], bundle["scaler"], bundle["features"]


def predict_email(text: str, model_path: str = "outputs/classifier.pkl") -> dict:
    """
    Παίρνει email text και επιστρέφει:
      - label     : "SCAM" ή "LEGIT"
      - confidence: πιθανότητα 0.0–1.0
      - features  : τα extracted features
    """
    model, scaler, feature_cols = load_model(model_path)

    features = extract_features(text)
    X = pd.DataFrame([features])[feature_cols].fillna(0)

    proba = model.predict_proba(X)[0]
    scam_prob = proba[1]
    label = "SCAM" if scam_prob >= 0.5 else "LEGIT"

    return {
        "label": label,
        "confidence": round(float(scam_prob), 4),
        "features": {k: features[k] for k in feature_cols},
    }


if __name__ == "__main__":
    # Quick test
    sample_scam = """
    Dear Beloved Friend,
    I am Prince Adebayo of Nigeria. I have $45 MILLION DOLLARS
    waiting for you!!! This is 100% confidential and URGENT.
    Please send your bank details IMMEDIATELY to claim your inheritance.
    God Bless You,
    Prince Adebayo
    """

    result = predict_email(sample_scam)
    print(f"Label     : {result['label']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Features  : {result['features']}")
