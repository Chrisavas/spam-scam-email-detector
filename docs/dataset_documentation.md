# Dataset & Preprocessing — Τεκμηρίωση (Άτομο 1)

## 1. Πηγή Δεδομένων

Το final dataset είναι ένα **consolidated 3-source dataset**:

1. **Synthetic dataset** (αυτογενή) — 386 emails
   - 4 κατηγορίες scam (Nigerian prince, lottery, romance, investment)
   - 25 templates legit emails
   - Λόγος: antivirus false positive κατά το κατέβασμα Kaggle corpus

2. **Enron Fraud Email Dataset** (real-world) — 17,249 emails (→ 11,048 μετά dedup)
   - Από τη Kaggle: https://www.kaggle.com/datasets/advaithsrao/enron-fraud-email-dataset
   - 644 fraud, 16,605 legitimate emails
   - Πραγματικά emails από το Enron scandal

3. **SpamAssassin Public Corpus** (real-world) — 3,000 emails
   - Από τη Kaggle: https://www.kaggle.com/datasets/ozlerhakan/spam-or-not-spam-dataset
   - 500 spam, 2,500 legitimate emails
   - Καθαρή, pre-processed corpus

**Τελικό merged dataset: 13,919 emails** (after deduplication across all 3 sources)

## 2. Σχήμα Δεδομένων (Schema)

### Raw dataset (`data/raw/emails.csv`)

| Στήλη | Τύπος | Περιγραφή |
|-------|-------|-----------|
| `text` | string | Το πλήρες σώμα του email (χωρίς headers) |
| `label` | int (0/1) | 0 = legitimate, 1 = scam/spam |

### Processed dataset (`data/processed/emails_features.csv`)

| Στήλη | Τύπος | Περιγραφή |
|-------|-------|-----------|
| `label` | int (0/1) | Ground truth label |
| `word_count` | int | Συνολικός αριθμός λέξεων (μετά tokenization) |
| `unique_words` | int | Αριθμός μοναδικών λέξεων (χωρίς stopwords) |
| `avg_word_length` | float | Μέσο μήκος λέξης (χωρίς stopwords) |
| `scam_keyword_count` | int | Πλήθος εμφανίσεων γνωστών scam-keywords (λίστα 18 φράσεων) |
| `caps_ratio` | float | Ποσοστό λέξεων >2 χαρακτήρων εντελώς σε ΚΕΦΑΛΑΙΑ |
| `exclamation_count` | int | Αριθμός "!" στο αρχικό κείμενο |
| `question_count` | int | Αριθμός "?" στο αρχικό κείμενο |
| `money_mentions` | int | Αναφορές χρηματικών ποσών (`$X`, `X million`, `X dollars` κλπ) |
| `cleaned_text` | string | Καθαρισμένο κείμενο (lowercase, χωρίς HTML/URLs/ειδικούς χαρακτήρες) |

## 3. Στατιστικά Final Dataset (3-Source)

```
Σύνολο emails      : 13,919
Spam/Fraud (1)     : 1,067  (7.7%)
Legit/Ham (0)      : 12,852 (92.3%)
Duplicates removed : ~128 (cross-source merging)
Missing values     : 0
```

### Διαχωριστική ισχύς features (μέσες τιμές ανά label)

| Feature | Legit (0) | Spam (1) |
|---------|-----------|----------|
| word_count | 284.1 | 248.9 |
| scam_keyword_count | 0.10 | 0.49 |
| exclamation_count | 1.22 | 2.08 |
| money_mentions | 1.43 | 0.91 |

### Ενδιαφέρουσες παρατηρήσεις

- **Balanced class distribution**: 7.7% spam/fraud είναι realistic για real-world email filtering
- **Diverse email patterns**: Συνδυασμός Enron (εταιρικών), Synthetic (template scams), SpamAssassin (community corpus)
- **Strong feature separation**: Spam emails έχουν 5x περισσότερα scam keywords και 1.7x περισσότερα exclamation marks
- **Robust dataset**: 13,919 emails από 3 ανεξάρτητες πηγές → less overfit risk

## 4. Deliverable Αρχεία

### Raw data
- `data/raw/emails.csv` — DEPRECATED (synthetic only)
- `data/raw/unified_emails.csv` — **FINAL** (Synthetic + Enron merged, 11,048 rows)
- `data/raw/generate_dataset.py` — script που δημιουργεί synthetic data
- `data/raw/merge_datasets.py` — script που κάνει merge δύο datasets

### Processed data
- `data/processed/emails_features.csv` — DEPRECATED
- `data/processed/unified_emails_features.csv` — **FINAL** (11,048 emails με 8 features, ready for ML)

## 5. Σημαντικές Αποφάσεις Σχεδιασμού

- **Tokenization**: χρησιμοποιήθηκε απλό regex tokenizer (`\b[a-zA-Z]+\b`) αντί για
  `nltk.word_tokenize`, ώστε το pipeline να είναι **πλήρως reproducible χωρίς
  εξωτερικές εξαρτήσεις** (NLTK `punkt_tab` data download). Αναφέρετέ το ως
  reproducibility decision στο report.
- **`money_mentions`** υπολογίζεται στο αρχικό (μη καθαρισμένο) κείμενο, γιατί η
  `clean_text()` αφαιρεί αριθμούς/σύμβολα `$` — bug που εντοπίστηκε και διορθώθηκε
  κατά το testing (καλό παράδειγμα για error analysis section).
- **Class imbalance** (64/36): ελαφρά ανισορροπία, διαχειρίσιμη με
  `class_weight="balanced"` στο classifier (ήδη έτοιμο στο `train.py`).

## 6. Επόμενα Βήματα (για Άτομο 2)

Το αρχείο `data/processed/emails_features.csv` είναι έτοιμο για:
```bash
python src/classifier/train.py --data data/processed/emails_features.csv
```
