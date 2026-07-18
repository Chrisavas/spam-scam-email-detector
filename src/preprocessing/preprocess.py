"""
preprocess.py — Email preprocessing & feature extraction
(Task 2: pipeline καθαρισμού και εξαγωγής χαρακτηριστικών από το κείμενο email)

ΒΗΜΑΤΑ:
  1. Φόρτωση raw email text (text, label)
  2. Καθαρισμός (HTML, URLs, ειδικοί χαρακτήρες, lowercasing)
  3. Εξαγωγή 8 αριθμητικών features (+ cleaned_text)
  4. Αποθήκευση σε processed CSV, έτοιμο για τον classifier (Task 4)

ΤΑ 8 FEATURES:
  Λεξικά (word_count, unique_words, avg_word_length), σήματα απάτης
  (scam_keyword_count), και σήματα "πίεσης" (caps_ratio, exclamation_count,
  question_count, money_mentions). Επιλέχθηκαν ελαφριά, ΕΡΜΗΝΕΥΣΙΜΑ features
  αντί για βαριά NLP (π.χ. NER), ώστε το μοντέλο να είναι εξηγήσιμο.
"""

import re
import pandas as pd
import nltk

# Σημείωση: χρησιμοποιούμε απλό regex tokenizer αντί για nltk.word_tokenize
# ώστε το pipeline να τρέχει χωρίς να χρειάζεται download εξωτερικών NLTK data
# (punkt_tab) — χρήσιμο όταν δεν υπάρχει internet access ή σε CI/CD.
from nltk.corpus import stopwords

# Κατεβάζουμε ΜΟΝΟ τα stopwords (μικρό corpus). Τον tokenizer (punkt) τον
# αποφεύγουμε επίτηδες -> λιγότερες εξαρτήσεις/downloads σε CI ή χωρίς internet.
nltk.download("stopwords", quiet=True)

# Αγγλικά stopwords: αφαιρούνται πριν μετρήσουμε unique_words/avg_word_length,
# ώστε τα features να μη "θορυβούνται" από κοινές λέξεις (the, and, of...).
STOP_WORDS = set(stopwords.words("english"))


def word_tokenize(text: str) -> list:
    """Απλό regex-based tokenizer (λέξεις μόνο, χωρίς punctuation)."""
    return re.findall(r"\b\w+\b", text.lower())

# ─────────────────────────────────────────────────────────────────────────────
# Λεξικό ενδεικτικών scam keywords (EN + GR), οργανωμένο ανά κατηγορία απάτης.
# Το feature scam_keyword_count μετρά πόσες από αυτές εμφανίζονται στο email.
# Καλύπτονται και ελληνικά με διάφορες καταλήξεις, ώστε να πιάνονται GR scams.
# ─────────────────────────────────────────────────────────────────────────────
SCAM_KEYWORDS = [
   # ── Αγγλικά: Urgency & Action ──
    "urgent", "immediately", "strictly confidential", "24 hours", "48 hours",
    "suspended", "blocked", "verify", "click here", "action required", 
    "warning", "alert", "confirm", "update your account", "login now",
    "unauthorized access", "security alert", "password reset",

    # ── Αγγλικά: Money & Prizes ──
    "million dollars", "billion", "usd", "gbp", "euros", "bank transfer",
    "wire transfer", "western union", "moneygram", "lottery winner", 
    "claim your prize", "jackpot", "sweepstakes", "compensation", "fund", 
    "risk free", "investment", "guaranteed returns", "invoice", "billing",

    # ── Αγγλικά: Identity & Romance ──
    "next of kin", "beneficiary", "inheritance", "nigerian prince", 
    "dying widow", "god bless", "kindly", "beloved", "my dear", "lonely", 
    "soulmate", "deployed", "military", "stranded", "gift cards", "hospital bill",

    # ── Αγγλικά: Tech, Crypto & Extortion ──
    "hack", "hacked", "hacker", "trojan", "malware", "spyware", "recorded you", 
    "webcam", "pay me", "bitcoin", "btc", "crypto", "wallet", "operating system", 
    "leak", "release your video", "porn", "adult website", "keylogger",

    # ── Ελληνικά: Επείγον & Δράση (με καταλήξεις) ──
    "επείγον", "επειγόντως", "εμπιστευτικό", "άμεσα", "προειδοποίηση", 
    "προσοχή", "αναστολή", "απενεργοποιηθεί", "απενεργοποίηση", "ακύρωση",
    "επιβεβαίωση", "επιβεβαιώστε", "ανανεώστε", "ενέργεια", "απαιτείται",
    "μπλοκαριστεί", "μπλοκαρισμένος", "κλειδωθεί", "κλειδωμένος", "προσωρινά",
    "σύνδεση", "σύνδεσης", "σύνδεσμο", "σύνδεσμος", "link", "κλικ", "πατήστε",

    # ── Ελληνικά: Χρήματα, Τράπεζες & Βραβεία ──
    "εκατομμύρια", "χιλιάδες", "ευρώ", "δολάρια", "κερδίσατε", "λαχείο", 
    "έπαθλο", "νικητής", "νικήτρια", "αποζημίωση", "κληρωθήκατε",
    "μεταφορά", "έμβασμα", "χρήματα", "λεφτά", "πληρωμή", "τιμολόγιο", "απόδειξη",
    "τράπεζα", "τράπεζας", "τραπεζικός", "τραπεζικό", "λογαριασμός", "λογαριασμό", 
    "λογαριασμού", "κάρτα", "κάρτας", "χρέωση", "επένδυση", "κέρδη", "κέρδος",

    # ── Ελληνικά: Tech, Crypto & Εκβιασμός ──
    "ιός", "κακόβουλο", "λογισμικό", "κάμερα", "κάμερας", "βίντεο", "οθόνη",
    "καταγράψει", "παρακολουθώ", "χακάρει", "χάκερ", "πρόσβαση", "διαρροή",
    "κρυπτονομίσματα", "κρυπτονόμισμα", "πορτοφόλι", "bitcoin", "btc",
    "κωδικός", "κωδικό", "κωδικούς", "στοιχεία", "στοιχείων", "ταυτοποίηση",
    "ασφάλεια", "ασφαλείας", "διαγραφεί", "οριστικά", "συσκευή", "λειτουργικό",

   # ── Ελληνικά: Ταυτότητα, Απάτη 419 (Nigerian Prince) & Κληρονομιά ──
    "κληρονομιά", "διαθήκη", "δικαιούχος", "συγγενής", "μακρινός συγγενής", 
    "νιγηριανός", "νιγηρίας", "πρίγκιπας", "πρίγκιπα", "εκλιπών", "εκλιπόντος",
    "απεβίωσε", "πέθανε", "δυστύχημα", "ατύχημα", "καρκίνο", "νοσοκομείο",
    "δικηγόρος", "νομικός εκπρόσωπος", "διευθυντής τράπεζας", "υπουργείο",
    "κεφάλαιο", "κεφάλαια", "τεράστιο ποσό", "ποσοστό", "προμήθεια", 
    "φιλανθρωπία", "ορφανοτροφείο", "χήρα", "βοήθεια", "θεός", "ευλογεί",
    "εμπιστευτικότητα", "άκρα μυστικότητα", "αξιότιμε", "φόρος", "τελωνείο",
]


def clean_text(text: str) -> str:
    """Αφαίρεση HTML, URLs, special chars και lowercasing."""
    text = re.sub(r"<[^>]+>", " ", text)          # HTML tags
    text = re.sub(r"http\S+|www\.\S+", " ", text)  # URLs
    text = re.sub(r"[^\w\s]", " ", text)      # Non-alpha
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

    # ── Ποσοστό ΚΕΦΑΛΑΙΩΝ λέξεων (>2 χαρ.): οι scammers συχνά "φωνάζουν". ──
    # Υπολογίζεται στο ΑΡΧΙΚΟ κείμενο (το clean_text έχει κάνει ήδη lowercase).
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
    # Defaults -> το ΤΕΛΙΚΟ dataset (13.919). Μπορούν να παρακαμφθούν με ορίσματα.
    parser.add_argument("--input",  default="data/raw/final_unified_emails.csv")
    parser.add_argument("--output", default="data/processed/final_unified_emails_features.csv")
    args = parser.parse_args()

    preprocess_dataset(args.input, args.output)
