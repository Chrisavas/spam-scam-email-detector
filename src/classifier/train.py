"""
train.py — Training & comparison of ML classifiers for scam/spam detection
(Task 4: design, training and evaluation of the classification model)

WHAT IT DOES:
  Trains and compares two models on the 8 numeric features:
    - Baseline : Multinomial Naive Bayes (simple, fast reference point)
    - Main     : Random Forest (better fraud detection — higher recall/ROC-AUC)

  Saves the final model (RF) together with the scaler and the feature names,
  so that predict.py can load it directly without retraining.

NOTE ON ACCURACY:
  Because of the imbalance (7.7% spam), accuracy is MISLEADING: a model that
  always predicts "Legit" reaches ~92% accuracy without detecting a single scam.
  That is why model selection is based on recall/ROC-AUC for the fraud class.
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


# The 8 features produced by preprocessing and "seen" by the model.
# They must be EXACTLY the same (and in the same order) as in predict.py,
# otherwise inference would read the wrong columns.
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
    """Reads the processed CSV and returns X (features) and y (label)."""
    df = pd.read_csv(path)
    # fillna(0): any missing features (e.g. from empty emails) -> 0, so training does not crash.
    X = df[FEATURE_COLS].fillna(0)
    y = df["label"]
    return X, y


def evaluate_model(model, X_test, y_test, model_name: str):
    """Prints full evaluation metrics (precision/recall/F1, ROC-AUC, confusion matrix)."""
    y_pred = model.predict(X_test)
    # predict_proba -> probability of the "Spam" class (column 1), for ROC-AUC.
    y_prob = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, "predict_proba")
        else None
    )

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    # target_names: shows "Legit"/"Spam" instead of 0/1 in the report.
    print(classification_report(y_test, y_pred, target_names=["Legit", "Spam"]))

    if y_prob is not None:
        auc = roc_auc_score(y_test, y_prob)
        print(f"  ROC-AUC: {auc:.4f}")

    cm = confusion_matrix(y_test, y_pred)
    print(f"  Confusion Matrix:\n{cm}")

    return y_pred


def train(data_path: str, model_output_path: str = "outputs/classifier.pkl"):
    print(f"[*] Loading processed data from: {data_path}")
    X, y = load_data(data_path)

    # 80/20 train/test split. stratify=y -> preserves the same 7.7% spam ratio
    # in both subsets. random_state=42 -> same split every time (reproducible).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # MinMaxScaler: Multinomial Naive Bayes requires NON-NEGATIVE input values,
    # so we bring every feature into [0,1]. (Random Forest needs no scaling.)
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    print(f"\n[*] Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"    Spam rate (train): {y_train.mean():.1%}")

    # ── Baseline: Naive Bayes (on the scaled data) ──
    # Expected to "fall" into the imbalance trap (predicting almost everything Legit).
    nb = MultinomialNB()
    nb.fit(X_train_scaled, y_train)
    evaluate_model(nb, X_test_scaled, y_test, "Baseline — Naive Bayes")

    # ── Main: Random Forest (on the raw data — trees do not need scaling) ──
    rf = RandomForestClassifier(
        n_estimators=200,          # enough trees for stability
        max_depth=10,              # limited depth -> avoids overfitting on the small % of fraud
        class_weight="balanced",   # heavier penalty for errors on the minority class (spam)
        random_state=42,           # reproducibility
        n_jobs=-1,                 # use all cores
    )
    rf.fit(X_train, y_train)
    evaluate_model(rf, X_test, y_test, "Main Model — Random Forest")

    # Feature importance: which features "weigh" most in the RF decision.
    importances = pd.Series(rf.feature_importances_, index=FEATURE_COLS)
    print("\n[*] Feature Importances (Random Forest):")
    print(importances.sort_values(ascending=False).to_string())

    # Save TOGETHER: model + scaler + feature names (in a single bundle),
    # so that predict.py has everything it needs for consistent inference.
    os.makedirs("outputs", exist_ok=True)
    with open(model_output_path, "wb") as f:
        pickle.dump({"model": rf, "scaler": scaler, "features": FEATURE_COLS}, f)

    print(f"\n[✓] Model saved: {model_output_path}")
    return rf, scaler


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train Spam Classifier")
    # Default -> the FINAL dataset (13,919 emails). Can be overridden with --data.
    parser.add_argument("--data",   default="data/processed/final_unified_emails_features.csv")
    parser.add_argument("--output", default="outputs/classifier.pkl")
    args = parser.parse_args()

    train(args.data, args.output)
