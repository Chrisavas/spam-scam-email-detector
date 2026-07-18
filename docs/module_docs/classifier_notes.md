### ML Classifier (Task 4)

Υπεύθυνος για τον σχεδιασμό, την επιλογή και την αξιολόγηση του μοντέλου μηχανικής μάθησης (ML Classifier) για τον διαχωρισμό των email (Spam/Legit).

**Βασικές Υλοποιήσεις:**

* **Διαχείριση Δεδομένων:** Πραγματοποιήθηκε 80/20 Train/Test split. Λόγω του έντονου class imbalance (τα spam ήταν μόνο το 7,7% του dataset των 13.919 emails), εφαρμόστηκε `stratified split` για τη διατήρηση της σωστής κατανομής και κανονικοποίηση (MinMaxScaler) για το baseline μοντέλο.
* **Εκπαίδευση Μοντέλων:**
  * Ανάπτυξη ενός **Baseline μοντέλου (Multinomial Naive Bayes)**, το οποίο ανέδειξε το πρόβλημα του imbalance (Recall 0%).
  * Ανάπτυξη του **Κύριου μοντέλου (Random Forest)** με χρήση της παραμέτρου `class_weight="balanced"` για την αυστηρότερη τιμωρία των λανθασμένων Spam.
* **Αξιολόγηση:** Εξαγωγή αναλυτικών μετρικών (Precision, Recall, F1-Score, Confusion Matrix, ROC-AUC). Το Random Forest επιλέχθηκε ως τελικό μοντέλο, επιτυγχάνοντας **ROC-AUC 0,815** και **Spam Recall 65%**.
* **Inference Pipeline:** Δημιουργία του `predict.py`, το οποίο δέχεται νέα emails, εξάγει δυναμικά τα features τους και επιστρέφει το τελικό label (SCAM/LEGIT) μαζί με το confidence score, τροφοδοτώντας έτσι το Generative AI σκέλος του συστήματος.

**Παραδοτέα:**
- `src/classifier/train.py` (αντί του ενιαίου classifier.py για καλύτερη δομή)
- `src/classifier/predict.py`
- `outputs/classifier.pkl`
- `docs/module_docs/metrics.md`
