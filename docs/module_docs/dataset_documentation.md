# Dataset & Preprocessing — Documentation

## 1. Data Sources

The final dataset is a **consolidated 3-source dataset**:

1. **Synthetic dataset** (self-generated) — 386 emails
   - 4 scam categories (Nigerian prince, lottery, romance, investment)
   - 25 legit email templates
   - Reason: antivirus false positive while downloading the Kaggle corpus

2. **Enron Fraud Email Dataset** (real-world)
   - From Kaggle: https://www.kaggle.com/datasets/advaithsrao/enron-fraud-email-dataset
   - Real emails from the Enron scandal (fraud + legitimate)

3. **SpamAssassin Public Corpus** (real-world)
   - From Kaggle: https://www.kaggle.com/datasets/ozlerhakan/spam-or-not-spam-dataset
   - Established corpus with spam + ham (legitimate)

**Final merged dataset: 13,919 emails** (after removing duplicates across all 3 sources)

## 2. Data Schema

### Raw dataset (`data/raw/final_unified_emails.csv`)

| Column | Type | Description |
|-------|-------|-----------|
| `text` | string | The full email body (without headers) |
| `label` | int (0/1) | 0 = legitimate, 1 = scam/spam |

### Processed dataset (`data/processed/final_unified_emails_features.csv`)

| Column | Type | Description |
|-------|-------|-----------|
| `label` | int (0/1) | Ground truth label |
| `word_count` | int | Total number of words (after tokenization) |
| `unique_words` | int | Number of unique words (excluding stopwords) |
| `avg_word_length` | float | Average word length (excluding stopwords) |
| `scam_keyword_count` | int | Number of occurrences of known scam keywords (extended EN+GR list) |
| `caps_ratio` | float | Share of words >2 characters written entirely in UPPERCASE |
| `exclamation_count` | int | Number of "!" in the original text |
| `question_count` | int | Number of "?" in the original text |
| `money_mentions` | int | Mentions of monetary amounts (`$X`, `€X`, `X million`, `X dollars`, `X ευρώ`, etc.) |
| `cleaned_text` | string | Cleaned text (lowercase, no HTML/URLs/special characters) |

## 3. Final Dataset Statistics (3-Source)

```
Total emails       : 13,919
Spam/Fraud (1)     : 1,067  (7.7%)
Legit/Ham (0)      : 12,852 (92.3%)
Missing values     : 0
```

### Discriminative power of the features (mean values per label)

| Feature | Legit (0) | Spam (1) |
|---------|-----------|----------|
| word_count | 284.1 | 248.9 |
| scam_keyword_count | 0.10 | 0.49 |
| exclamation_count | 1.22 | 2.08 |
| money_mentions | 1.43 | 0.91 |

### Observations

- **Realistic but imbalanced distribution:** 7.7% spam/fraud is realistic for real-world email filtering, but it is the core classification difficulty (which is why `class_weight="balanced"` is used in the classifier).
- **Diversity:** a combination of Enron (corporate), Synthetic (template scams) and SpamAssassin (community corpus).
- **Discriminative features:** spam emails have on average ~5x more scam keywords and ~1.7x more exclamation marks.
- **Robust dataset:** 13,919 emails from 3 independent sources → lower risk of overfitting.

## 4. Deliverable Files

### Raw data
- `data/raw/final_unified_emails.csv` — **FINAL** (all 3 sources, 13,919 rows)
- `data/raw/generate_dataset.py` — script that creates the synthetic data
- `data/raw/merge_datasets.py` — script that merges the 3 datasets
- (`emails.csv`, `unified_emails.csv` — DEPRECATED, archived)

### Processed data
- `data/processed/final_unified_emails_features.csv` — **FINAL** (13,919 emails with 8 features, ML-ready)
- (`emails_features.csv`, `unified_emails_features.csv` — DEPRECATED, archived)

## 5. Key Design Decisions

- **Tokenization:** a simple regex tokenizer (`\b\w+\b`) was used instead of
  `nltk.word_tokenize`, so that the pipeline is **fully reproducible without
  external dependencies** (the NLTK `punkt_tab` data download) and also supports
  Greek characters. This is documented as a reproducibility decision in the report.
- **`money_mentions`** is computed on the original (uncleaned) text, because
  `clean_text()` strips digits and the `$`/`€` symbols — a bug that was found and
  fixed during testing (a good example for the error analysis section).
- **Class imbalance (92/8 — 7.7% spam):** severe but realistic imbalance,
  handled with `class_weight="balanced"` in the classifier (already set up in `train.py`).

## 6. Next Steps (classifier training)

The file `data/processed/final_unified_emails_features.csv` is ready for:
```bash
python src/classifier/train.py --data data/processed/final_unified_emails_features.csv
```
