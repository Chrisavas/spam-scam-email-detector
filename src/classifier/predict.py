"""
predict.py — Inference: πρόβλεψη scam/legit για νέα emails
(Task 4: το inference στάδιο του classifier, τροφοδοτεί το pipeline/responder)

ΤΙ ΚΑΝΕΙ:
  Φορτώνει το εκπαιδευμένο μοντέλο (outputs/classifier.pkl), εξάγει δυναμικά τα
  features ενός νέου email μέσω του preprocessing, και επιστρέφει label + confidence.
  Είναι ο "κρίκος" που καλεί το pipeline: αν το αποτέλεσμα είναι SCAM, ενεργοποιείται
  ο responder.
"""

import pickle
import sys
import os

# Το src/ (γονιός αυτού του φακέλου) μπαίνει στο path ώστε να βρεθεί το
# preprocessing package (χρησιμοποιούμε τα ΙΔΙΑ features με την εκπαίδευση).
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from preprocessing.preprocess import extract_features
import pandas as pd

# Απόλυτο path για το model -> λειτουργεί ανεξάρτητα από το cwd (από όπου κι αν
# τρέξει ο χρήστης το script, βρίσκει το outputs/classifier.pkl).
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
_DEFAULT_MODEL_PATH = os.path.join(_PROJECT_ROOT, "outputs", "classifier.pkl")


def load_model(model_path: str = None):
    """Φορτώνει το bundle (model + scaler + features) από το .pkl."""
    if model_path is None:
        model_path = _DEFAULT_MODEL_PATH
    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
    return bundle["model"], bundle["scaler"], bundle["features"]


def predict_email(text: str, model_path: str = None) -> dict:
    """
    Παίρνει email text και επιστρέφει:
      - label     : "SCAM" ή "LEGIT"
      - confidence: πιθανότητα να είναι scam (0.0–1.0)
      - features  : τα extracted features (για διαφάνεια/debugging)
    """
    model, scaler, feature_cols = load_model(model_path)

    # Ίδια εξαγωγή features με την εκπαίδευση -> ίδιο "λεξιλόγιο" εισόδου.
    features = extract_features(text)
    # DataFrame με τις στήλες στη ΣΩΣΤΗ σειρά (feature_cols) που περιμένει το μοντέλο.
    X = pd.DataFrame([features])[feature_cols].fillna(0)

    proba = model.predict_proba(X)[0]
    scam_prob = proba[1]                       # πιθανότητα κλάσης "Spam"
    # Κατώφλι 0.5: >=0.5 -> SCAM. Ευνοεί το recall (αμυντικό φίλτρο).
    label = "SCAM" if scam_prob >= 0.5 else "LEGIT"

    return {
        "label": label,
        "confidence": round(float(scam_prob), 4),
        "features": {k: features[k] for k in feature_cols},
    }


if __name__ == "__main__":
    # Γρήγορο test με ένα δείγμα scam email.
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
