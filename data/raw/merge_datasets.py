"""
merge_datasets.py — Ενοποίηση 3 datasets σε ένα τελικό unified dataset
(Task 1: consolidated dataset από συνθετικά + πραγματικά corpora)

ΤΙ ΚΑΝΕΙ:
  Διαβάζει και τα 3 datasets, τα φέρνει σε ΚΟΙΝΟ schema (text, label), αφαιρεί
  διπλότυπα (case-insensitive), ανακατεύει και σώζει το τελικό αρχείο.

ΠΗΓΕΣ:
  1. Synthetic (emails.csv)          — 386 emails, πλήρης έλεγχος ετικετών
  2. Enron Fraud Dataset             — πραγματικά εταιρικά emails (ρεαλισμός γλώσσας)
  3. SpamAssassin Public Corpus      — καθιερωμένο corpus spam + ham

  Ο συνδυασμός συνθετικών + πραγματικών εξισορροπεί τον ΕΛΕΓΧΟ των labels με τον
  ΡΕΑΛΙΣΜΟ, μειώνοντας τον κίνδυνο υπερβολικά "καθαρών" προτύπων.

ΑΝΘΕΚΤΙΚΟΤΗΤΑ:
  Οι loaders ανιχνεύουν αυτόματα το σωστό text/label column (τα Kaggle datasets
  έχουν διαφορετικά ονόματα στηλών) και χαρτογραφούν string labels (fraud/ham/...)
  σε 0/1, ώστε το script να δουλεύει χωρίς χειροκίνητη προσαρμογή.

OUTPUT: data/raw/final_unified_emails.csv  (schema: text, label)
"""

import pandas as pd
import os
from pathlib import Path

# Paths to the three datasets
RAW_DATA_DIR = "data/raw"
SYNTHETIC_CSV = os.path.join(RAW_DATA_DIR, "emails.csv")  # Our generated one (already OK)
ENRON_CSV = os.path.join(RAW_DATA_DIR, "enron_fraud.csv")  # To be uploaded
SPAMASSASSIN_CSV = os.path.join(RAW_DATA_DIR, "spam_or_not_spam.csv")  # To be uploaded

# Τελικό αρχείο εξόδου: το consolidated dataset και των 3 πηγών.
OUTPUT_CSV = os.path.join(RAW_DATA_DIR, "final_unified_emails.csv")


# --- LOADERS: κάθε ένας φέρνει την πηγή του στο κοινό schema (text, label) ---
def load_synthetic():
    """Load our synthetic dataset (already in correct format: text, label)."""
    print("[1/3] Φόρτωση synthetic dataset...")
    df = pd.read_csv(SYNTHETIC_CSV)
    print(f"      ✓ {len(df)} emails")
    return df


def load_enron():
    """
    Load Enron Fraud Dataset.
    Expected format varies, but typically has columns like:
    - 'email_body' or 'text' (content)
    - 'is_fraud' or 'fraud' or 'label' (binary label)
    
    This function handles common variants.
    """
    print("[2/3] Φόρτωση Enron Fraud Dataset...")
    if not os.path.exists(ENRON_CSV):
        print(f"      ✗ File not found: {ENRON_CSV}")
        return None
    
    df = pd.read_csv(ENRON_CSV)
    
    # Detect text column
    text_col = None
    for col in ['email_body', 'body', 'text', 'message', 'content']:
        if col in df.columns:
            text_col = col
            break
    
    # Detect label column
    label_col = None
    for col in ['is_fraud', 'fraud', 'label', 'is_scam']:
        if col in df.columns:
            label_col = col
            break
    
    if not text_col or not label_col:
        print(f"      ✗ Could not detect text/label columns. Found: {df.columns.tolist()}")
        return None
    
    df = df[[text_col, label_col]].copy()
    df.columns = ['text', 'label']
    
    # Ensure label is 0/1 (if it's boolean, convert)
    if df['label'].dtype == 'bool':
        df['label'] = df['label'].astype(int)
    
    # Handle non-binary labels (e.g., if label is 'fraud'/'not fraud' string)
    if df['label'].dtype == 'object':
        label_map = {
            'fraud': 1, 'scam': 1, 'spam': 1, 'yes': 1, 'true': 1, '1': 1,
            'legitimate': 0, 'legit': 0, 'ham': 0, 'no': 0, 'false': 0, '0': 0
        }
        df['label'] = df['label'].str.lower().map(label_map)
    
    df = df.dropna(subset=['text', 'label'])
    print(f"      ✓ {len(df)} emails (text_col={text_col}, label_col={label_col})")
    return df


def load_spamassassin():
    """
    Load SpamAssassin Public Corpus (as CSV).
    Expected format:
    - 'email' or 'text' (content)
    - 'label' or 'spam' (0=ham, 1=spam)
    """
    print("[3/3] Φόρτωση SpamAssassin Public Corpus...")
    if not os.path.exists(SPAMASSASSIN_CSV):
        print(f"      ✗ File not found: {SPAMASSASSIN_CSV}")
        return None
    
    df = pd.read_csv(SPAMASSASSIN_CSV)
    
    # Detect text column
    text_col = None
    for col in ['email', 'text', 'message', 'body', 'content']:
        if col in df.columns:
            text_col = col
            break
    
    # Detect label column
    label_col = None
    for col in ['label', 'spam', 'is_spam']:
        if col in df.columns:
            label_col = col
            break
    
    if not text_col or not label_col:
        print(f"      ✗ Could not detect text/label columns. Found: {df.columns.tolist()}")
        return None
    
    df = df[[text_col, label_col]].copy()
    df.columns = ['text', 'label']
    
    # Ensure label is 0/1
    if df['label'].dtype == 'bool':
        df['label'] = df['label'].astype(int)
    if df['label'].dtype == 'object':
        label_map = {
            'spam': 1, 'scam': 1, 'fraud': 1, 'yes': 1, 'true': 1, '1': 1,
            'ham': 0, 'legitimate': 0, 'legit': 0, 'no': 0, 'false': 0, '0': 0
        }
        df['label'] = df['label'].str.lower().map(label_map)
    
    df = df.dropna(subset=['text', 'label'])
    print(f"      ✓ {len(df)} emails (text_col={text_col}, label_col={label_col})")
    return df


def merge_all():
    """
    Ενοποίηση: φορτώνει ό,τι dataset ειναι διαθέσιμο, τα συνενώνει, κάνει dedup,
    ανακάτεμα και αποθήκευση. Αν λείπει το Enron ή το SpamAssassin (δεν βρεθεί
    το αρχείο), απλώς παραλείπεται -> το script δεν σπάει.
    """
    dfs = []
    
    # Load synthetic (always available)
    df_synthetic = load_synthetic()
    if df_synthetic is not None:
        dfs.append(df_synthetic)
    
    # Load Enron (if available)
    df_enron = load_enron()
    if df_enron is not None:
        dfs.append(df_enron)
    
    # Load SpamAssassin (if available)
    df_spam = load_spamassassin()
    if df_spam is not None:
        dfs.append(df_spam)
    
    if not dfs:
        raise Exception("No datasets loaded!")
    
    # Merge all dataframes
    print("\n[*] Ενοποίηση datasets...")
    df_merged = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicates (by text, case-insensitive)
    # dedup με βάση το κείμενο σε lowercase, ώστε να μην υπερεκπροσωπείται καμία πηγή.
    print(f"    Πριν dedup: {len(df_merged)} emails")
    df_merged['text_lower'] = df_merged['text'].str.lower()
    df_merged = df_merged.drop_duplicates(subset=['text_lower'], keep='first')
    df_merged = df_merged.drop('text_lower', axis=1)
    print(f"    Μετά dedup: {len(df_merged)} emails")
    
    # Ανακάτεμα με σταθερό seed -> ίδια σειρά κάθε φορά (reproducible split αργότερα).
    df_merged = df_merged.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    df_merged.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[✓] Unified dataset: {OUTPUT_CSV}")
    
    # Print statistics
    print("\n=== ΣΤΑΤΙΣΤΙΚΑ ===")
    print(f"Σύνολο emails: {len(df_merged)}")
    print(f"Scam/Spam (1): {(df_merged['label']==1).sum()}")
    print(f"Legit/Ham (0): {(df_merged['label']==0).sum()}")
    print(f"Ratio: {(df_merged['label']==1).sum() / len(df_merged):.1%} spam/scam")
    
    return df_merged


if __name__ == "__main__":
    merge_all()
