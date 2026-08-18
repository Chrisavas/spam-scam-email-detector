"""
preprocess.py — Email preprocessing & feature extraction
(Task 2: pipeline for cleaning and extracting features from email text)

STEPS:
  1. Load raw email text (text, label)
  2. Clean (HTML, URLs, special characters, lowercasing)
  3. Extract 8 numeric features (+ cleaned_text)
  4. Save to a processed CSV, ready for the classifier (Task 4)

THE 8 FEATURES:
  Lexical (word_count, unique_words, avg_word_length), fraud signals
  (scam_keyword_count), and "pressure" signals (caps_ratio, exclamation_count,
  question_count, money_mentions). Lightweight, INTERPRETABLE features were chosen
  instead of heavy NLP (e.g. NER), so that the model stays explainable.
"""

import re
import pandas as pd
import nltk

# Note: we use a simple regex tokenizer instead of nltk.word_tokenize so that the
# pipeline runs without needing to download external NLTK data (punkt_tab) —
# useful when there is no internet access or in CI/CD.
from nltk.corpus import stopwords

# We download ONLY the stopwords (a small corpus). We deliberately avoid the
# tokenizer (punkt) -> fewer dependencies/downloads in CI or offline.
nltk.download("stopwords", quiet=True)

# English stopwords: removed before we count unique_words/avg_word_length, so that
# the features are not "noised" by common words (the, and, of...).
STOP_WORDS = set(stopwords.words("english"))


def word_tokenize(text: str) -> list:
    """Simple regex-based tokenizer (words only, no punctuation)."""
    return re.findall(r"\b\w+\b", text.lower())

# ─────────────────────────────────────────────────────────────────────────────
# Dictionary of indicative scam keywords (EN + GR), organised by fraud category.
# The scam_keyword_count feature counts how many of these appear in the email.
# Greek terms with various inflections are included as well, so that GR scams are
# caught too. NOTE: the Greek entries are DETECTION DATA, not prose — they are
# intentionally left untranslated, since translating them would break matching on
# Greek-language scam emails.
# ─────────────────────────────────────────────────────────────────────────────
SCAM_KEYWORDS = [
   # ── English: Urgency & Action ──
    "urgent", "immediately", "strictly confidential", "24 hours", "48 hours",
    "suspended", "blocked", "verify", "click here", "action required",
    "warning", "alert", "confirm", "update your account", "login now",
    "unauthorized access", "security alert", "password reset",

    # ── English: Money & Prizes ──
    "million dollars", "billion", "usd", "gbp", "euros", "bank transfer",
    "wire transfer", "western union", "moneygram", "lottery winner",
    "claim your prize", "jackpot", "sweepstakes", "compensation", "fund",
    "risk free", "investment", "guaranteed returns", "invoice", "billing",

    # ── English: Identity & Romance ──
    "next of kin", "beneficiary", "inheritance", "nigerian prince",
    "dying widow", "god bless", "kindly", "beloved", "my dear", "lonely",
    "soulmate", "deployed", "military", "stranded", "gift cards", "hospital bill",

    # ── English: Tech, Crypto & Extortion ──
    "hack", "hacked", "hacker", "trojan", "malware", "spyware", "recorded you",
    "webcam", "pay me", "bitcoin", "btc", "crypto", "wallet", "operating system",
    "leak", "release your video", "porn", "adult website", "keylogger",

    # ── Greek: Urgency & Action (with inflections) ──
    "επείγον", "επειγόντως", "εμπιστευτικό", "άμεσα", "προειδοποίηση",
    "προσοχή", "αναστολή", "απενεργοποιηθεί", "απενεργοποίηση", "ακύρωση",
    "επιβεβαίωση", "επιβεβαιώστε", "ανανεώστε", "ενέργεια", "απαιτείται",
    "μπλοκαριστεί", "μπλοκαρισμένος", "κλειδωθεί", "κλειδωμένος", "προσωρινά",
    "σύνδεση", "σύνδεσης", "σύνδεσμο", "σύνδεσμος", "link", "κλικ", "πατήστε",

    # ── Greek: Money, Banking & Prizes ──
    "εκατομμύρια", "χιλιάδες", "ευρώ", "δολάρια", "κερδίσατε", "λαχείο",
    "έπαθλο", "νικητής", "νικήτρια", "αποζημίωση", "κληρωθήκατε",
    "μεταφορά", "έμβασμα", "χρήματα", "λεφτά", "πληρωμή", "τιμολόγιο", "απόδειξη",
    "τράπεζα", "τράπεζας", "τραπεζικός", "τραπεζικό", "λογαριασμός", "λογαριασμό",
    "λογαριασμού", "κάρτα", "κάρτας", "χρέωση", "επένδυση", "κέρδη", "κέρδος",

    # ── Greek: Tech, Crypto & Extortion ──
    "ιός", "κακόβουλο", "λογισμικό", "κάμερα", "κάμερας", "βίντεο", "οθόνη",
    "καταγράψει", "παρακολουθώ", "χακάρει", "χάκερ", "πρόσβαση", "διαρροή",
    "κρυπτονομίσματα", "κρυπτονόμισμα", "πορτοφόλι", "bitcoin", "btc",
    "κωδικός", "κωδικό", "κωδικούς", "στοιχεία", "στοιχείων", "ταυτοποίηση",
    "ασφάλεια", "ασφαλείας", "διαγραφεί", "οριστικά", "συσκευή", "λειτουργικό",

   # ── Greek: Identity, 419 fraud (Nigerian Prince) & Inheritance ──
    "κληρονομιά", "διαθήκη", "δικαιούχος", "συγγενής", "μακρινός συγγενής",
    "νιγηριανός", "νιγηρίας", "πρίγκιπας", "πρίγκιπα", "εκλιπών", "εκλιπόντος",
    "απεβίωσε", "πέθανε", "δυστύχημα", "ατύχημα", "καρκίνο", "νοσοκομείο",
    "δικηγόρος", "νομικός εκπρόσωπος", "διευθυντής τράπεζας", "υπουργείο",
    "κεφάλαιο", "κεφάλαια", "τεράστιο ποσό", "ποσοστό", "προμήθεια",
    "φιλανθρωπία", "ορφανοτροφείο", "χήρα", "βοήθεια", "θεός", "ευλογεί",
    "εμπιστευτικότητα", "άκρα μυστικότητα", "αξιότιμε", "φόρος", "τελωνείο",
]


def clean_text(text: str) -> str:
    """Removes HTML, URLs, special chars and lowercases."""
    text = re.sub(r"<[^>]+>", " ", text)          # HTML tags
    text = re.sub(r"http\S+|www\.\S+", " ", text)  # URLs
    text = re.sub(r"[^\w\s]", " ", text)      # Non-alpha
    text = re.sub(r"\s+", " ", text).strip()        # Extra whitespace
    return text.lower()


def extract_features(text: str) -> dict:
    """
    Extracts features from the email text.
    Returns a dict with all the features for the ML model.
    """
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    tokens_no_stop = [t for t in tokens if t not in STOP_WORDS]

    # ── Basic features ──
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

    # ── Ratio of UPPERCASE words (>2 chars): scammers often "shout". ──
    # Computed on the ORIGINAL text (clean_text has already lowercased everything).
    original_words = text.split()
    caps_ratio = (
        sum(1 for w in original_words if w.isupper() and len(w) > 2)
        / len(original_words)
        if original_words else 0
    )

    # ── Exclamation / urgency signals ──
    exclamation_count = text.count("!")
    question_count = text.count("?")

    # ── Money mentions ── (on the original text, before $ and digits are stripped in clean_text)
    money_mentions = len(re.findall(
        r"[\$€][\d,]+|\d+\s*(?:million|billion|usd|dollars|gbp|euro|euros|ευρώ|ευρω)", text, flags=re.IGNORECASE
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
    Loads the raw dataset, extracts features and saves a processed CSV.

    The input CSV must have at least:
      - 'text' column  : the email body
      - 'label' column : 1 = spam/scam, 0 = legitimate
    """
    print(f"[*] Loading dataset from: {input_path}")
    df = pd.read_csv(input_path)

    assert "text" in df.columns, "Missing 'text' column"
    assert "label" in df.columns, "Missing 'label' column"

    print(f"[*] {len(df)} emails loaded.")
    print(f"    Spam: {df['label'].sum()} | Legit: {(df['label'] == 0).sum()}")

    print("[*] Extracting features...")
    features = df["text"].apply(extract_features)
    features_df = pd.DataFrame(features.tolist())

    result = pd.concat([df[["label"]], features_df], axis=1)

    result.to_csv(output_path, index=False)
    print(f"[✓] Processed dataset saved: {output_path}")
    return result


# ─────────────────────────────────────────
# Standalone run
# ─────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Email Preprocessing Pipeline")
    # Defaults -> the FINAL dataset (13,919). Can be overridden with arguments.
    parser.add_argument("--input",  default="data/raw/final_unified_emails.csv")
    parser.add_argument("--output", default="data/processed/final_unified_emails_features.csv")
    args = parser.parse_args()

    preprocess_dataset(args.input, args.output)
