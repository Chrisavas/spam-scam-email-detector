"""
train.py — ML Spam/Scam Classifier Training
Αρμόδιο άτομο: Άτομο 2

Εκπαιδεύει δύο models και συγκρίνει:
  - Baseline : Naive Bayes (απλό, γρήγορο)
  - Main     : Random Forest (καλύτερο accuracy)

Αποθηκεύει το καλύτερο model για χρήση από το pipeline.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.preprocessing import MinMaxScaler


# ─── Features που χρησιμοποιεί το model ───
FEATURE_COLS = [
    "word_count",
    "unique_words",
    "avg_word_length",
    "scam_keyword_count",
    "caps_ratio",
    "exclamation_count",
    "question_count",
    "money_mentions",
]


def load_data(path: str):
    df = pd.read_csv(path)
    X = df[FEATURE_COLS].fillna(0)
    y = df["label"]
    return X, y


def evaluate_model(model, X_test, y_test, model_name: str):
    """Εκτυπώνει πλήρη evaluation metrics."""
    y_pred = model.predict(X_test)
    y_prob = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, "predict_proba")
        else None
    )

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    print(classification_report(y_test, y_pred, target_names=["Legit", "Spam"]))

    if y_prob is not None:
        auc = roc_auc_score(y_test, y_prob)
        print(f"  ROC-AUC: {auc:.4f}")

    cm = confusion_matrix(y_test, y_pred)
    print(f"  Confusion Matrix:\n{cm}")

    return y_pred


def train(data_path: str, model_output_path: str = "outputs/classifier.pkl"):
    print(f"[*] Φόρτωση processed data από: {data_path}")
    X, y = load_data(data_path)

    # Train/test split (80/20, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Normalize για Naive Bayes (χρειάζεται non-negative)
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    print(f"\n[*] Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"    Spam rate (train): {y_train.mean():.1%}")

    # ── Baseline: Naive Bayes ──
    nb = MultinomialNB()
    nb.fit(X_train_scaled, y_train)
    evaluate_model(nb, X_test_scaled, y_test, "Baseline — Naive Bayes")

    # ── Main: Random Forest ──
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",  # Αντιμετωπίζει class imbalance
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    evaluate_model(rf, X_test, y_test, "Main Model — Random Forest")

    # Feature importance
    importances = pd.Series(rf.feature_importances_, index=FEATURE_COLS)
    print("\n[*] Feature Importances (Random Forest):")
    print(importances.sort_values(ascending=False).to_string())

    # Αποθήκευση model + scaler
    os.makedirs("outputs", exist_ok=True)
    with open(model_output_path, "wb") as f:
        pickle.dump({"model": rf, "scaler": scaler, "features": FEATURE_COLS}, f)

    print(f"\n[✓] Model αποθηκεύτηκε: {model_output_path}")
    return rf, scaler


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train Spam Classifier")
    parser.add_argument("--data",   default="data/processed/emails_features.csv")
    parser.add_argument("--output", default="outputs/classifier.pkl")
    args = parser.parse_args()

    train(args.data, args.output)
