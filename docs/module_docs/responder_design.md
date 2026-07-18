# Responder — Design & Safety

Κείμενο τεκμηρίωσης για το report. Καλύπτει Task 5 (generative responder),
Task 6 (multi-turn) και τη συμβολή στο Task 7 (safety/ethics). Οι σχεδιαστικές
επιλογές είναι ευθυγραμμισμένες με τις αρχές της Διάλεξης 7 (Responsible AI).

## 1. Ρόλος στο σύστημα

Ο responder είναι το **δεύτερο στάδιο** του pipeline. Ενεργοποιείται **μόνο** όταν
ο binary classifier σημάνει ένα email ως scam πάνω από το threshold.
Σκοπός του δεν είναι να βοηθήσει τον scammer, αλλά να τον κρατήσει απασχολημένο με
πλασματική συνομιλία (scambaiting), εκτρέποντας χρόνο μακριά από πραγματικά θύματα.

Διεπαφή (αμετάβλητη ως προς pipeline/app):
`generate_reply(scam_email, conversation_history, provider) -> {reply, scam_type, turn, history, safety}`

## 2. Scam-type detection & τόνος ανά τύπο (Task 5)

Το dataset είναι binary (legit/scam), χωρίς ετικέτα τύπου. Επομένως ο responder
**εξάγει μόνος του τον τύπο** με διαφανή (explainable) keyword scoring:
`nigerian_prince, lottery, romance, investment, phishing` και **`generic`** ως
fallback για τα messy real-world spam (Enron/SpamAssassin) που δεν ταιριάζουν σε
γνωστή κατηγορία.

Κάθε τύπος αντιστοιχεί σε **διακριτή persona** (τόνος + τακτική χρονοτριβής +
ιδιαίτερο χαρακτηριστικό). Π.χ. στο `investment` ο «επενδυτής» έχει $47 και
μπερδεύει το Bitcoin με «Bitchoin»· στο `phishing` ζητάει από τον ίδιο τον scammer
να επιβεβαιώσει στοιχεία πρώτος, ώστε να μην εισαχθεί ποτέ πραγματικό credential.

## 3. Multi-turn συμπεριφορά (Task 6)

Το `conversation_history` μεταφέρεται μεταξύ των turns. Δύο σχεδιαστικές επιλογές
σταθερότητας:
- **Κλείδωμα τύπου στο 1ο turn:** ο `scam_type` ανιχνεύεται από το *πρώτο* email
  και παραμένει σταθερός, ώστε η persona να μην «παίζει» αν ο scammer αλλάξει θέμα.
- **Καθαρό history:** η συνάρτηση δουλεύει σε αντίγραφο και δεν τροποποιεί in-place
  τη λίστα του caller.

Το `transcript.py` εξάγει ολόκληρη τη συνομιλία σε markdown, έτοιμο ως παράδειγμα
για το report.

## 4. Safety / output guardrail (Task 7)

Αντί να βασιστούμε μόνο στις οδηγίες του persona, εφαρμόζουμε **explicit output
checks** — ακριβώς η αρχή «Output checks» / «Block unsafe actions» της Διάλεξης 7.
Η `safety_check()` ελέγχει κάθε παραγόμενη απάντηση *πριν* επιστραφεί:

| Έλεγχος | Ενέργεια | Σύνδεση με κίνδυνο |
|---|---|---|
| Απειλές / κακοποίηση | block → ασφαλές fallback | αποφυγή harassment |
| Πραγματικό ραντεβού / διεύθυνση | redact + flag | **escalation risk** (αναφέρεται στην εκφώνηση) |
| IBAN, κάρτα, SSN, BTC/ETH wallet | redact + flag | διαρροή/χρήση πραγματικών στοιχείων |
| Email / τηλέφωνο | redact + flag | data handling / PII |
| Κενή απάντηση | safe fallback | σταθερότητα |

Επιπλέον, **separate data from instructions**: το email του scammer περνά ως
*untrusted data* μέσα σε `<scam_email>` tags, με ρητή οδηγία στο system prompt να
μην εκτελούνται εντολές που κρύβονται μέσα του (άμυνα σε prompt injection — βλ.
«Prompt manipulation», Διάλεξη 7).

## 5. Reproducibility & demo

Υποστηρίζονται τρεις providers: `anthropic` (Claude), `openai`, και **`mock`**
(deterministic, χωρίς API key). Ο mock provider επιτρέπει το demo και τα unit
tests να τρέχουν **offline σε οποιοδήποτε μηχάνημα**, χωρίς κόστος ή κλειδιά —
χρήσιμο για grading και CI.

## 6. Όρια & μελλοντικές βελτιώσεις

- Η ανίχνευση τύπου είναι keyword-based· ένας μικρός supervised type-classifier θα
  ήταν πιο ανθεκτικός.
- Το guardrail είναι heuristic (regex)· δεν πιάνει κάθε πιθανή διαρροή.
- Σκόπιμα **δεν** γίνεται καμία αυτόματη αποστολή/απάντηση σε πραγματικό mailbox·
  το σύστημα παράγει μόνο draft απαντήσεις σε **simulated** emails. Πραγματική
  ανάπτυξη θα απαιτούσε human-in-the-loop έγκριση (Διάλεξη 7: «Ask for human
  approval»).

## 7. Αρχεία (deliverables)

- `src/responder/responder.py` — core responder + `safety_check` + providers
- `src/responder/transcript.py` — markdown exporter των συνομιλιών
- `tests/test_responder.py` — unit tests (mock provider, offline)
- `docs/responder_design.md` — αυτό το κείμενο
