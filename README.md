# spam-scam-email-detector
AI-powered spam and scam email detection system with  automated generative AI responses. Built for cybersecurity research. 13.9K labeled emails from 3 real-world sources.  Includes ML classifier, NLP preprocessing, and multi-turn chatbot.


# Spam & Scam Email Detection System

## Overview
AI-driven system to detect spam/scam emails and auto-reply with scambaiting.

## Features
- ML classifier (Naive Bayes + Random Forest)
- Generative AI responder (Claude/OpenAI)
- Multi-turn conversation support

## Quick Start
```bash
git clone <spam-scam-email-detector>
cd scam-ai-detector
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/classifier/train.py --data data/raw/final_unified_emails.csv
```

## Dataset
- 13,919 emails from 3 sources
- 7.7% spam/fraud, 92.3% legitimate
- See docs/dataset_documentation.md

## Team
- Άτομο 1: Dataset & Preprocessing
- Άτομο 2: ML Classifier
- Άτομο 3: AI Responder
- Άτομο 4: Pipeline & Demo
- Άτομο 5: Research & Ethics
- Άτομο 6: Report & Coordination
