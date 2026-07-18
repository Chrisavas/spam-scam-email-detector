# Dataset & Preprocessing — Τεκμηρίωση

## 1. Πηγή Δεδομένων

Το final dataset είναι ένα **consolidated 3-source dataset**:

1. **Synthetic dataset** (αυτογενή) — 386 emails
   - 4 κατηγορίες scam (Nigerian prince, lottery, romance, investment)
   - 25 templates legit emails
   - Λόγος: antivirus false positive κατά το κατέβασμα Kaggle corpus

2. **Enron Fraud Email Dataset** (real-world)
   - Από τη Kaggle: https://www.kaggle.com/datasets/advaithsrao/enron-fraud-email-dataset
   - Πραγματικά emails από το Enron scandal (fraud + legitimate)

3. **SpamAssassin Public Corpus** (real-world)
   - Από τη Kaggle: https://www.kaggle.com/datasets/ozlerhakan/spam-or-not-spam-dataset
   - Καθιερωμένο corpus με spam + ham (legitimate)

**Τελικό merged dataset: 13.919 emails** (μετά την απαλοιφή διπλοτύπων και στις 3 πηγές)

## 2. Σχήμα Δεδομένων (Schema)

### Raw dataset (`data/raw/final_unified_emails.csv`)

| Στήλη | Τύπος | Περιγραφή |
|-------|-------|-----------|
| `text` | string | Το πλήρες σώμα του email (χωρίς headers) |
| `label` | int (0/1) | 0 = legitimate, 1 = scam/spam |

### Processed dataset (`data/processed/final_unified_emails_features.csv`)

| Στήλη | Τύπος | Περιγραφή |
|-------|-------|-----------|
| `label` | int (0/1) | Ground truth label |
| `word_count` | int | Συνολικός αριθμός λέξεων (μετά tokenization) |
| `unique_words` | int | Αριθμός μοναδικών λέξεων (χωρίς stopwords) |
| `avg_word_length` | float | Μέσο μήκος λέξης (χωρίς stopwords) |
| `scam_keyword_count` | int | Πλήθος εμφανίσεων γνωστών scam-keywords (εκτεταμένη λίστα EN+GR) |
| `caps_ratio` | float | Ποσοστό λέξεων >2 χαρακτήρων εντελώς σε ΚΕΦΑΛΑΙΑ |
| `exclamation_count` | int | Αριθμός "!" στο αρχικό κείμενο |
| `question_count` | int | Αριθμός "?" στο αρχικό κείμενο |
| `money_mentions` | int | Αναφορές χρηματικών ποσών (`$X`, `€X`, `X million`, `X dollars`, `X ευρώ` κλπ) |
| `cleaned_text` | string | Καθαρισμένο κείμενο (lowercase, χωρίς HTML/URLs/ειδικούς χαρακτήρες) |

## 3. Στατιστικά Final Dataset (3-Source)

```
Σύνολο emails      : 13.919
Spam/Fraud (1)     : 1.067  (7,7%)
Legit/Ham (0)      : 12.852 (92,3%)
Missing values     : 0
```

### Διαχωριστική ισχύς features (μέσες τιμές ανά label)

| Feature | Legit (0) | Spam (1) |
|---------|-----------|----------|
| word_count | 284.1 | 248.9 |
| scam_keyword_count | 0.10 | 0.49 |
| exclamation_count | 1.22 | 2.08 |
| money_mentions | 1.43 | 0.91 |

### Παρατηρήσεις

- **Ρεαλιστική αλλά μη ισορροπημένη κατανομή (imbalanced):** το 7,7% spam/fraud είναι ρεαλιστικό για πραγματικό email filtering, αλλά συνιστά τη βασική δυσκολία ταξινόμησης (γι' αυτό χρησιμοποιείται `class_weight="balanced"` στον classifier).
- **Ποικιλομορφία:** συνδυασμός Enron (εταιρικών), Synthetic (template scams) και SpamAssassin (community corpus).
- **Διαχωριστικά features:** τα spam emails έχουν κατά μέσο όρο ~5x περισσότερα scam keywords και ~1,7x περισσότερα θαυμαστικά.
- **Ανθεκτικό dataset:** 13.919 emails από 3 ανεξάρτητες πηγές → μικρότερος κίνδυνος overfit.

## 4. Deliverable Αρχεία

### Raw data
- `data/raw/final_unified_emails.csv` — **FINAL** (και οι 3 πηγές, 13.919 rows)
- `data/raw/generate_dataset.py` — script που δημιουργεί τα synthetic data
- `data/raw/merge_datasets.py` — script που ενοποιεί τα 3 datasets
- (`emails.csv`, `unified_emails.csv` — DEPRECATED, στο αρχείο)

### Processed data
- `data/processed/final_unified_emails_features.csv` — **FINAL** (13.919 emails με 8 features, έτοιμο για ML)
- (`emails_features.csv`, `unified_emails_features.csv` — DEPRECATED, στο αρχείο)

## 5. Σημαντικές Αποφάσεις Σχεδιασμού

- **Tokenization:** χρησιμοποιήθηκε απλός regex tokenizer (`\b\w+\b`) αντί για
  `nltk.word_tokenize`, ώστε το pipeline να είναι **πλήρως reproducible χωρίς
  εξωτερικές εξαρτήσεις** (NLTK `punkt_tab` data download) και να υποστηρίζει και
  ελληνικούς χαρακτήρες. Αναφέρεται ως reproducibility decision στο report.
- **`money_mentions`** υπολογίζεται στο αρχικό (μη καθαρισμένο) κείμενο, γιατί η
  `clean_text()` αφαιρεί αριθμούς/σύμβολα `$`/`€` — bug που εντοπίστηκε και
  διορθώθηκε κατά το testing (καλό παράδειγμα για error analysis section).
- **Class imbalance (92/8 — 7,7% spam):** έντονη αλλά ρεαλιστική ανισορροπία,
  διαχειρίσιμη με `class_weight="balanced"` στον classifier (ήδη έτοιμο στο `train.py`).

## 6. Επόμενα Βήματα (classifier training)

Το αρχείο `data/processed/final_unified_emails_features.csv` είναι έτοιμο για:
```bash
python src/classifier/train.py --data data/processed/final_unified_emails_features.csv
```
