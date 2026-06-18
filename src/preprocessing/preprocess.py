"""
preprocess.py — Email Preprocessing Pipeline
Αρμόδιο άτομο: Άτομο 1

Βήματα:
  1. Φόρτωση raw email text
  2. Καθαρισμός (HTML, special chars, κλπ)
  3. Feature extraction
  4. Αποθήκευση σε processed CSV
"""

import re
import pandas as pd
import nltk

# Σημείωση: χρησιμοποιούμε απλό regex tokenizer αντί για nltk.word_tokenize
# ώστε το pipeline να τρέχει χωρίς να χρειάζεται download εξωτερικών NLTK data
# (punkt_tab) — χρήσιμο όταν δεν υπάρχει internet access ή σε CI/CD.
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)

STOP_WORDS = set(stopwords.words("english"))


def word_tokenize(text: str) -> list:
    """Απλό regex-based tokenizer (λέξεις μόνο, χωρίς punctuation)."""
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())

# ─────────────────────────────────────────
# Scam keywords που χρησιμοποιούν scammers
# ─────────────────────────────────────────
SCAM_KEYWORDS = [
    "urgent", "confidential", "million dollars", "bank transfer",
    "next of kin", "beneficiary", "inheritance", "lottery winner",
    "claim your prize", "western union", "wire transfer",
    "nigerian prince", "dying widow", "god bless", "100% risk free",
    "kindly", "strictly confidential", "beloved",
]


def clean_text(text: str) -> str:
    """Αφαίρεση HTML, URLs, special chars και lowercasing."""
    text = re.sub(r"<[^>]+>", " ", text)          # HTML tags
    text = re.sub(r"http\S+|www\.\S+", " ", text)  # URLs
    text = re.sub(r"[^a-zA-Z\s]", " ", text)       # Non-alpha
    text = re.sub(r"\s+", " ", text).strip()        # Extra whitespace
    return text.lower()


def extract_features(text: str) -> dict:
    """
    Εξάγει features από το email text.
    Επιστρέφει dict με όλα τα features για το ML model.
    """
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    tokens_no_stop = [t for t in tokens if t not in STOP_WORDS]

    # ── Βασικά features ──
    word_count = len(tokens)
    unique_words = len(set(tokens_no_stop))
    avg_word_length = (
        sum(len(w) for w in tokens_no_stop) / len(tokens_no_stop)
        if tokens_no_stop else 0
    )

    # ── Scam keyword count ──
    scam_keyword_count = sum(
        1 for kw in SCAM_KEYWORDS if kw in cleaned
    )

    # ── Capitalization signals (scammers SHOUTING) ──
    original_words = text.split()
    caps_ratio = (
        sum(1 for w in original_words if w.isupper() and len(w) > 2)
        / len(original_words)
        if original_words else 0
    )

    # ── Exclamation / urgency signals ──
    exclamation_count = text.count("!")
    question_count = text.count("?")

    # ── Money mentions ── (στο αρχικό text, πριν αφαιρεθούν $ και ψηφία στο clean_text)
    money_mentions = len(re.findall(
        r"\$[\d,]+|\d+\s*(?:million|billion|usd|dollars|gbp)", text, flags=re.IGNORECASE
    ))

    return {
        "word_count": word_count,
        "unique_words": unique_words,
        "avg_word_length": round(avg_word_length, 3),
        "scam_keyword_count": scam_keyword_count,
        "caps_ratio": round(caps_ratio, 3),
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "money_mentions": money_mentions,
        "cleaned_text": cleaned,
    }


def preprocess_dataset(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Φορτώνει το raw dataset, εξάγει features και αποθηκεύει processed CSV.

    Το input CSV πρέπει να έχει τουλάχιστον:
      - 'text' column  : το body του email
      - 'label' column : 1 = spam/scam, 0 = legitimate
    """
    print(f"[*] Φόρτωση dataset από: {input_path}")
    df = pd.read_csv(input_path)

    assert "text" in df.columns, "Λείπει η στήλη 'text'"
    assert "label" in df.columns, "Λείπει η στήλη 'label'"

    print(f"[*] {len(df)} emails φορτώθηκαν.")
    print(f"    Spam: {df['label'].sum()} | Legit: {(df['label'] == 0).sum()}")

    print("[*] Εξαγωγή features...")
    features = df["text"].apply(extract_features)
    features_df = pd.DataFrame(features.tolist())

    result = pd.concat([df[["label"]], features_df], axis=1)

    result.to_csv(output_path, index=False)
    print(f"[✓] Processed dataset αποθηκεύτηκε: {output_path}")
    return result


# ─────────────────────────────────────────
# Standalone run
# ─────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Email Preprocessing Pipeline")
    parser.add_argument("--input",  default="data/raw/emails.csv")
    parser.add_argument("--output", default="data/processed/emails_features.csv")
    args = parser.parse_args()

    preprocess_dataset(args.input, args.output)
