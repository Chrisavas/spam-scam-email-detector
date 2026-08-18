### ML Classifier (Task 4)

Responsible for the design, selection and evaluation of the machine learning model (ML Classifier) used to separate emails (Spam/Legit).

**Key implementations:**

* **Data handling:** An 80/20 Train/Test split was performed. Due to the severe class imbalance (spam accounted for only 7.7% of the 13,919-email dataset), a `stratified split` was applied to preserve the correct distribution, along with normalisation (MinMaxScaler) for the baseline model.
* **Model training:**
  * Development of a **Baseline model (Multinomial Naive Bayes)**, which exposed the imbalance problem (Recall 0%).
  * Development of the **Main model (Random Forest)** using the `class_weight="balanced"` parameter to penalise misclassified Spam more heavily.
* **Evaluation:** Extraction of detailed metrics (Precision, Recall, F1-Score, Confusion Matrix, ROC-AUC). Random Forest was selected as the final model, achieving **ROC-AUC 0.815** and **Spam Recall 65%**.
* **Inference pipeline:** Creation of `predict.py`, which takes new emails, dynamically extracts their features and returns the final label (SCAM/LEGIT) together with a confidence score, thereby feeding the Generative AI part of the system.

**Deliverables:**
- `src/classifier/train.py` (instead of a single classifier.py, for better structure)
- `src/classifier/predict.py`
- `outputs/classifier.pkl`
- `docs/module_docs/metrics.md`
