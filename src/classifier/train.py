"""
train.py — Εκπαίδευση & σύγκριση ML classifiers για scam/spam detection
(Task 4: σχεδιασμός, εκπαίδευση και αξιολόγηση του μοντέλου ταξινόμησης)

ΤΙ ΚΑΝΕΙ:
  Εκπαιδεύει και συγκρίνει δύο μοντέλα πάνω στα 8 αριθμητικά features:
    - Baseline : Multinomial Naive Bayes (απλό, γρήγορο σημείο αναφοράς)
    - Main     : Random Forest (καλύτερη ανίχνευση απάτης — υψηλότερο recall/ROC-AUC)

  Αποθηκεύει το τελικό μοντέλο (RF) μαζί με τον scaler και τα ονόματα των features,
  ώστε να το φορτώνει απευθείας το predict.py χωρίς επανεκπαίδευση.

ΣΗΜΕΙΩΣΗ ΓΙΑ ΤΟ ACCURACY:
  Λόγω της ανισορροπίας (7,7% spam), το accuracy είναι ΠΑΡΑΠΛΑΝΗΤΙΚΟ: ένα μοντέλο
  που προβλέπει πάντα "Legit" πιάνει ~92% accuracy χωρίς να εντοπίσει καμία απάτη.
  Γι' αυτό η επιλογή μοντέλου γίνεται με βάση recall/ROC-AUC στην κλάση της απάτης.
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


# Τα 8 features που παράγει το preprocessing και "βλέπει" το μοντέλο.
# Πρέπει να είναι ΑΚΡΙΒΩΣ ίδια (και στη σειρά) με του predict.py, αλλιώς το
# inference θα διαβάζει λάθος στήλες.
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
    """Διαβάζει το processed CSV και επιστρέφει X (features) και y (label)."""
    df = pd.read_csv(path)
    # fillna(0): τυχόν κενά features (π.χ. από άδεια emails) -> 0, ώστε να μη σκάσει η εκπαίδευση.
    X = df[FEATURE_COLS].fillna(0)
    y = df["label"]
    return X, y


def evaluate_model(model, X_test, y_test, model_name: str):
    """Εκτυπώνει πλήρη evaluation metrics (precision/recall/F1, ROC-AUC, confusion matrix)."""
    y_pred = model.predict(X_test)
    # predict_proba -> πιθανότητα της κλάσης "Spam" (στήλη 1), για το ROC-AUC.
    y_prob = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, "predict_proba")
        else None
    )

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    # target_names: εμφανίζει "Legit"/"Spam" αντί για 0/1 στο report.
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

    # Train/test split 80/20. stratify=y -> διατηρεί την ίδια αναλογία 7,7% spam
    # και στα δύο υποσύνολα. random_state=42 -> ίδιο split κάθε φορά (reproducible).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # MinMaxScaler: ο Multinomial Naive Bayes απαιτεί ΜΗ ΑΡΝΗΤΙΚΕΣ τιμές εισόδου,
    # οπότε φέρνουμε κάθε feature στο [0,1]. (Ο Random Forest δεν χρειάζεται scaling.)
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    print(f"\n[*] Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"    Spam rate (train): {y_train.mean():.1%}")

    # ── Baseline: Naive Bayes (πάνω στα scaled δεδομένα) ──
    # Αναμένεται να "πέσει" στην παγίδα του imbalance (να προβλέπει σχεδόν τα πάντα Legit).
    nb = MultinomialNB()
    nb.fit(X_train_scaled, y_train)
    evaluate_model(nb, X_test_scaled, y_test, "Baseline — Naive Bayes")

    # ── Main: Random Forest (πάνω στα raw δεδομένα — τα δέντρα δεν θέλουν scaling) ──
    rf = RandomForestClassifier(
        n_estimators=200,          # αρκετά δέντρα για σταθερότητα
        max_depth=10,              # περιορισμένο βάθος -> αποφυγή overfit στο μικρό % απάτης
        class_weight="balanced",   # βαρύτερη ποινή στα λάθη της μειοψηφικής κλάσης (spam)
        random_state=42,           # αναπαραγωγιμότητα
        n_jobs=-1,                 # χρήση όλων των πυρήνων
    )
    rf.fit(X_train, y_train)
    evaluate_model(rf, X_test, y_test, "Main Model — Random Forest")

    # Feature importance: ποια features "βαραίνουν" περισσότερο στην απόφαση του RF.
    importances = pd.Series(rf.feature_importances_, index=FEATURE_COLS)
    print("\n[*] Feature Importances (Random Forest):")
    print(importances.sort_values(ascending=False).to_string())

    # Αποθήκευση ΜΑΖΙ: model + scaler + ονόματα features (σε ένα bundle),
    # ώστε το predict.py να έχει ό,τι χρειάζεται για συνεπές inference.
    os.makedirs("outputs", exist_ok=True)
    with open(model_output_path, "wb") as f:
        pickle.dump({"model": rf, "scaler": scaler, "features": FEATURE_COLS}, f)

    print(f"\n[✓] Model αποθηκεύτηκε: {model_output_path}")
    return rf, scaler


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train Spam Classifier")
    # Default -> το ΤΕΛΙΚΟ dataset (13.919 email). Μπορεί να παρακαμφθεί με --data.
    parser.add_argument("--data",   default="data/processed/final_unified_emails_features.csv")
    parser.add_argument("--output", default="outputs/classifier.pkl")
    args = parser.parse_args()

    train(args.data, args.output)
