# 🛡️ ScamAI — AI-Driven Spam Detection & Scam Engagement System

> **MSc Project — Advanced Artificial Intelligence & Cybersecurity** · Semester Project 1

A **two-stage** system for fighting online fraud:

1. **Classifier** → detects scam/spam emails using Machine Learning.
2. **Responder** → replies to scammers with Generative AI (*scambaiting*), keeping them busy and away from real victims.

> ⚠️ **Academic / simulated system.** It does not send emails, does not interact with real scammers and does not store any personal data. All conversations are simulated.

---

## ✨ Key features

- **Model comparison:** Naive Bayes (baseline) vs Random Forest, 8 interpretable features, `class_weight="balanced"` to handle the class imbalance (7.7% spam).
- **Responder with offline mock mode:** runs end-to-end with no API key and no cost. Optionally, a real provider (Anthropic Claude) is supported via `.env`.
- **Safety guardrails:** an output check that **redacts** real PII / IBANs / cards / wallets and **blocks** meeting requests and threats — before any reply leaves the system.
- **Anti prompt-injection:** the scammer's email is passed as *untrusted data* inside `<scam_email>` tags.
- **Multi-turn:** the scam type is "locked in" on the first message so the persona stays consistent.

---

## 🧭 Architecture

```
email ──▶ [Preprocessing] ──▶ [Classifier] ──scam?──▶ [Responder] ──▶ [safety_check] ──▶ reply
           8 features         NB / RF        ≥0.5      persona          redact/block
                                              │
                                              └── legit ──▶ (no reply)
```

---

## 📁 Structure

```
scam-ai/
├── data/
│   ├── raw/                                   # Raw datasets (git-ignored)
│   └── processed/
│       └── final_unified_emails_features.csv  # ✅ FINAL dataset (13,919 emails)
├── src/
│   ├── preprocessing/preprocess.py            # cleaning + feature extraction
│   ├── classifier/    train.py · predict.py   # ML (NB + RF)
│   ├── responder/     responder.py · transcript.py   # GenAI + safety + transcript export
│   └── pipeline/      pipeline.py · app.py     # end-to-end + Streamlit demo
├── tests/             test_preprocessing.py · test_responder.py
├── outputs/           classifier.pkl
├── docs/              documentation + final report (.docx/.md)
├── requirements.txt · .env.example · .gitignore
├── logo.png                    #  Light mode logo
├── logo_dark.png               #  Dark mode logo
└── README.md
```

---

## ⚙️ Setup

```bash
git clone https://github.com/Chrisavas/spam-scam-email-detector.git
cd scam-ai
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
cp .env.example .env        # Windows: copy .env.example .env   (optional — it also runs offline)
```

---

## ▶️ Usage

```bash
# 1) Train the classifier (NB + RF) on the FINAL dataset
python src/classifier/train.py --data data/processed/final_unified_emails_features.csv

# 2) Sample prediction (inference)
python src/classifier/predict.py

# 3) End-to-end / multi-turn demo
python src/pipeline/pipeline.py --demo
python src/pipeline/pipeline.py --input "Your scam email text here"

# 4) Streamlit demo UI
streamlit run src/pipeline/app.py
```

> ℹ️ **Dataset:** `train.py` already defaults to the final dataset, so it also runs bare (`python src/classifier/train.py`). The `--data` flag above is given simply for clarity.
> **Provider:** without a `.env`, the responder runs with the `mock` provider (offline, no key). For real replies, set `AI_PROVIDER=anthropic` (or `openai`/`gemini`) in `.env` along with the corresponding API key.

---

## 🧪 Tests

```bash
pytest -q      # offline (mock provider) — no API key needed
```

---

## 📊 Results (final dataset, 13,919 emails, 20% test)

| Metric (Scam class) | Naive Bayes | Random Forest |
|---|---|---|
| Precision | 0.00 | 0.23 |
| Recall | 0.00 | 0.65 |
| F1 | 0.00 | 0.33 |
| ROC-AUC | 0.575 | **0.815** |

Random Forest was selected as the final model: in a defensive filter, **recall** takes priority (no scam should slip through). Full analysis, charts and the legal/ethical framework: `docs/ScamAI_Final_Report_EL.docx`.

---

## ⚖️ Legal / ethical framework

The final report covers GDPR (Reg. 2016/679), the AI Act (Reg. 2024/1689, **Article 50** — transparency), NIS2, Directive 2013/40/EU (cybercrime), the Greek **Law 4624/2019** & **Article 9A of the Constitution**, as well as an ethical analysis of the "deception paradox".

---

## 👥 Team

| Role | Responsibility |
|---|---|
| Member 1 | Dataset & Preprocessing |
| Member 2 | ML Classifier |
| Member 3 | Generative AI Responder |
| Member 4 | Pipeline & Demo UI |
| Member 5 | Literature Review & Ethics |
| Member 6 | Report & Coordination |

---

## 📚 Datasets & Reproduction

The final dataset (13,919 emails) is derived from 3 sources: the **Enron Fraud Email Dataset** (Kaggle), the **SpamAssassin Public Corpus** (Kaggle) and **synthetic data**.

The datasets are git-ignored (large files). To rebuild them from scratch:

```bash
# 1) Download from Kaggle and place in data/raw/:
#    enron_fraud.csv, spam_or_not_spam.csv
# 2) Generate the synthetic data and merge:
python data/raw/generate_dataset.py     # -> data/raw/emails.csv
python data/raw/merge_datasets.py       # -> data/raw/final_unified_emails.csv
# 3) Feature extraction -> data/processed/final_unified_emails_features.csv
```

The ready-made `outputs/classifier.pkl` allows the results to be verified **without** retraining.

## 🚀 Streamlit Demo

To run the interactive UI:

```bash
streamlit run src/pipeline/app.py
```

**Features:**
- 📧 Analyze scam/legitimate emails
- 🎯 Real-time classification & type detection
- 🤖 Multi-turn AI responses (scambaiting)
- 📊 Feature breakdown & visualizations
- 🛡️ Safety guardrails
- 📄 Export transcripts
- ⚙️ Adjustable settings (threshold, provider, theme)
