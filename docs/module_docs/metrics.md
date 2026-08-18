# Model Evaluation & Metrics Report

**Purpose:** Evaluation of machine learning models for separating Legit from Spam/Scam emails.

## 1. Dataset Overview
The model was trained and evaluated on the final unified dataset.
* **Total size:** 13,919 emails
* **Train Set (80%):** 11,135 emails
* **Test Set (20%):** 2,784 emails
* **Class distribution:** Severe class imbalance, with Spam/Scam emails making up only 7.7% of the total (stratified split).

## 2. Model Comparison

Two models were evaluated based on their performance on the Test Set (2,784 samples). The evaluation focused on the metrics of the `Spam` class, given the nature of the problem.

| Model | ROC-AUC | Spam Recall | Spam Precision | Spam F1-Score | Overall Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline (Naive Bayes)** | 0.575 | 0.00 | 0.00 | 0.00 | 0.92 |
| **Main (Random Forest)** | 0.815 | 0.65 | 0.23 | 0.33 | 0.80 |

### 2.1 Baseline Model: Multinomial Naive Bayes
* **Behaviour:** Naive Bayes fell into the class imbalance trap (majority class trap). Although it achieved a high Overall Accuracy (92%), this is misleading, since the model effectively predicted that *all* emails were Legit.
* **Result:** It failed to detect even a single Spam email (Recall 0%), making it unsuitable for the purpose of the system.

### 2.2 Main Model: Random Forest
To address the imbalance, the `class_weight="balanced"` parameter was used, which imposes a heavier penalty on misclassified Spam.
* **Behaviour:** The model acquired strong discriminative ability, as shown by the ROC-AUC (0.815).
* **Detection (Recall):** It managed to detect 65% of the actual Spam emails (138 out of 213 in the Test Set).
* **Precision:** Precision came in at 23%. To achieve higher Recall on such imbalanced data, the model became more sensitive, increasing False Positives (475 Legit emails were classified as Spam).

## 3. Conclusion and Final Choice
**Random Forest** was clearly selected as the final model (`classifier.pkl`). Despite the relatively low precision, our system aims at proactive defence (scambaiting). Therefore, it is preferable to have a higher Spam Recall (0.65), so that we intercept a satisfactory number of scammers and feed them into the Generative AI responder.
