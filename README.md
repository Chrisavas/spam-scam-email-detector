# 🛡️ ScamAI — AI-Driven Spam Detection & Scam Engagement System

> **MSc Project — Προηγμένη Τεχνητή Νοημοσύνη & Κυβερνοασφάλεια** · Semester Project 1

Σύστημα **δύο σταδίων** για την καταπολέμηση της ηλεκτρονικής απάτης:

1. **Classifier** → εντοπίζει scam/spam emails με Μηχανική Μάθηση.
2. **Responder** → απαντά στους scammers με Generative AI (*scambaiting*), κρατώντας τους απασχολημένους μακριά από πραγματικά θύματα.

> ⚠️ **Ακαδημαϊκό / προσομοιωμένο σύστημα.** Δεν αποστέλλει emails, δεν αλληλεπιδρά με πραγματικούς απατεώνες και δεν αποθηκεύει προσωπικά δεδομένα. Όλες οι συνομιλίες είναι simulated.

---

## ✨ Βασικά χαρακτηριστικά

- **Σύγκριση μοντέλων:** Naive Bayes (baseline) vs Random Forest, 8 ερμηνεύσιμα features, `class_weight="balanced"` για την ανισορροπία κλάσεων (7,7% spam).
- **Responder με offline mock mode:** πλήρης εκτέλεση χωρίς API key/κόστος. Προαιρετικά, υποστηρίζεται πραγματικός provider (Anthropic Claude) μέσω `.env`.
- **Safety guardrails:** έλεγχος εξόδου που **αποκρύπτει (redacts)** πραγματικά PII / IBAN / κάρτες / wallets και **μπλοκάρει** ραντεβού & απειλές — πριν φύγει οποιαδήποτε απάντηση.
- **Anti prompt-injection:** το email του scammer περνά ως *μη έμπιστο δεδομένο* μέσα σε `<scam_email>` tags.
- **Multi-turn:** ο τύπος απάτης «κλειδώνει» στο 1ο μήνυμα ώστε η persona να μένει σταθερή.

---

## 🧭 Αρχιτεκτονική

```
email ──▶ [Preprocessing] ──▶ [Classifier] ──scam?──▶ [Responder] ──▶ [safety_check] ──▶ reply
           8 features         NB / RF        ≥0.5      persona          redact/block
                                              │
                                              └── legit ──▶ (no reply)
```

---

## 📁 Δομή

```
scam-ai/
├── data/
│   ├── raw/                                   # Raw datasets (git-ignored)
│   └── processed/
│       └── final_unified_emails_features.csv  # ✅ ΤΕΛΙΚΟ dataset (13.919 email)
├── src/
│   ├── preprocessing/preprocess.py            # καθαρισμός + feature extraction
│   ├── classifier/    train.py · predict.py   # ML (NB + RF)
│   ├── responder/     responder.py · transcript.py   # GenAI + safety + transcript export
│   └── pipeline/      pipeline.py · app.py     # end-to-end + Streamlit demo
├── tests/             test_preprocessing.py · test_responder.py
├── outputs/           classifier.pkl
├── docs/              τεκμηρίωση + τελική αναφορά (.docx/.md)
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
cp .env.example .env        # Windows: copy .env.example .env   (προαιρετικό — τρέχει και offline)
```

---

## ▶️ Χρήση

```bash
# 1) Εκπαίδευση classifier (NB + RF) στο ΤΕΛΙΚΟ dataset
python src/classifier/train.py --data data/processed/final_unified_emails_features.csv

# 2) Δοκιμαστική πρόβλεψη (inference)
python src/classifier/predict.py

# 3) End-to-end / multi-turn demo
python src/pipeline/pipeline.py --demo
python src/pipeline/pipeline.py --input "Your scam email text here"

# 4) Streamlit demo UI
streamlit run src/pipeline/app.py
```

> ℹ️ **Dataset:** το `train.py` κάνει ήδη default στο τελικό dataset, οπότε τρέχει και σκέτο (`python src/classifier/train.py`). Το `--data` παραπάνω δίνεται απλώς για σαφήνεια.
> **Provider:** χωρίς `.env` ο responder τρέχει με τον `mock` (offline, χωρίς key). Για πραγματικές απαντήσεις βάλε στο `.env` `AI_PROVIDER=anthropic` (ή `openai`/`gemini`) και το αντίστοιχο API key.

---

## 🧪 Tests

```bash
pytest -q      # offline (mock provider) — χωρίς API key
```

---

## 📊 Αποτελέσματα (τελικό dataset, 13.919 email, 20% test)

| Μετρική (κλάση Απάτη) | Naive Bayes | Random Forest |
|---|---|---|
| Precision | 0,00 | 0,23 |
| Recall | 0,00 | 0,65 |
| F1 | 0,00 | 0,33 |
| ROC-AUC | 0,575 | **0,815** |

Ο Random Forest επιλέχθηκε ως τελικό μοντέλο: σε αμυντικό φίλτρο προτεραιότητα έχει το **recall** (να μην ξεφεύγουν τα scam). Πλήρη ανάλυση, γραφήματα και νομικό/ηθικό πλαίσιο: `docs/ScamAI_Final_Report_EL.docx`.

---

## ⚖️ Νομικό / ηθικό πλαίσιο

Η τελική αναφορά καλύπτει GDPR (Καν. 2016/679), AI Act (Καν. 2024/1689, **Άρθρο 50** — διαφάνεια), NIS2, Οδηγία 2013/40/ΕΕ (κυβερνοέγκλημα), ελληνικό **Ν. 4624/2019** & **Άρθρο 9Α Συντάγματος**, καθώς και ηθική ανάλυση του «παραδόξου του δόλου».

---

## 👥 Ομάδα

| Ρόλος | Αρμοδιότητα |
|---|---|
| Άτομο 1 | Dataset & Preprocessing |
| Άτομο 2 | ML Classifier |
| Άτομο 3 | Generative AI Responder |
| Άτομο 4 | Pipeline & Demo UI |
| Άτομο 5 | Literature Review & Ethics |
| Άτομο 6 | Report & Coordination |

---

## 📚 Datasets & Αναπαραγωγή

Το τελικό dataset (13.919 email) προκύπτει από 3 πηγές: **Enron Fraud Email Dataset** (Kaggle), **SpamAssassin Public Corpus** (Kaggle) και **συνθετικά δεδομένα**.

Τα datasets είναι git-ignored (μεγάλα αρχεία). Για να τα ξαναφτιάξεις από την αρχή:

```bash
# 1) Κατέβασε από Kaggle και βάλε στο data/raw/:
#    enron_fraud.csv, spam_or_not_spam.csv
# 2) Παρήγαγε τα συνθετικά και ενοποίησε:
python data/raw/generate_dataset.py     # -> data/raw/emails.csv
python data/raw/merge_datasets.py       # -> data/raw/final_unified_emails.csv
# 3) Εξαγωγή features -> data/processed/final_unified_emails_features.csv
```

Το έτοιμο `outputs/classifier.pkl` επιτρέπει επαλήθευση των αποτελεσμάτων **χωρίς** επανεκπαίδευση.

## 🚀 Streamlit Demo

Για να τρέξεις το interactive UI:

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
