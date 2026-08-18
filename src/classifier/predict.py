"""
predict.py — Inference: scam/legit prediction for new emails
(Task 4: the inference stage of the classifier, feeding the pipeline/responder)

WHAT IT DOES:
  Loads the trained model (outputs/classifier.pkl), dynamically extracts the
  features of a new email via preprocessing, and returns a label + confidence.
  It is the "link" called by the pipeline: if the result is SCAM, the responder
  is triggered.
"""

import pickle
import sys
import os

# src/ (the parent of this folder) is added to the path so that the
# preprocessing package can be found (we use the SAME features as in training).
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from preprocessing.preprocess import extract_features
import pandas as pd

# Absolute path for the model -> works regardless of the cwd (wherever the user
# runs the script from, it finds outputs/classifier.pkl).
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
_DEFAULT_MODEL_PATH = os.path.join(_PROJECT_ROOT, "outputs", "classifier.pkl")


def load_model(model_path: str = None):
    """Loads the bundle (model + scaler + features) from the .pkl file."""
    if model_path is None:
        model_path = _DEFAULT_MODEL_PATH
    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
    return bundle["model"], bundle["scaler"], bundle["features"]


def predict_email(text: str, model_path: str = None) -> dict:
    """
    Takes email text and returns:
      - label     : "SCAM" or "LEGIT"
      - confidence: probability of being a scam (0.0–1.0)
      - features  : the extracted features (for transparency/debugging)
    """
    model, scaler, feature_cols = load_model(model_path)

    # Same feature extraction as in training -> same input "vocabulary".
    features = extract_features(text)
    # DataFrame with the columns in the CORRECT order (feature_cols) expected by the model.
    X = pd.DataFrame([features])[feature_cols].fillna(0)

    proba = model.predict_proba(X)[0]
    scam_prob = proba[1]                       # probability of the "Spam" class
    # Threshold 0.5: >=0.5 -> SCAM. Favours recall (defensive filter).
    label = "SCAM" if scam_prob >= 0.5 else "LEGIT"

    return {
        "label": label,
        "confidence": round(float(scam_prob), 4),
        "features": {k: features[k] for k in feature_cols},
    }


if __name__ == "__main__":
    # Quick test with a sample scam email.
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
