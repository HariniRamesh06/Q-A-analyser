# 🧠 Keyword-Based Quiz (ML-style) with OCR

A lightweight ML-style quiz app that scores free-text or handwritten answers using keyword/phrase matching, synonyms, and weights. Built with Streamlit for a clean, interactive UI.

## ✨ Features

✅ Type your answer or upload a handwritten answer (OCR)

✅ Keyword matching with synonyms (|) and weights (:number)

✅ Per-question scoring and overall percentage

✅ Downloadable results CSV

✅ Easy to extend and customize questions

✅ Optional keyword highlighting in results (future upgrade)

## 🔧 Installation & Run

1.Clone the repo:

git clone https://github.com/YourUsername/keyword-quiz-ocr.git
cd keyword-quiz-ocr

2.Install dependencies:

pip install -r requirements.txt

3.Install Tesseract OCR engine:

Windows: UB Mannheim build
macOS: brew install tesseract
Linux: sudo apt install tesseract-ocr
Ensure eng.traineddata exists in tessdata folder.

4.Run the app:

streamlit run app.py


## 🗂️ Data format
`data/questions.csv` must include:
- `question` (text)
- `keywords` (semicolon-separated specs)

Keyword spec syntax:
- `phrase` (weight 1)
- `alt1|alt2` (alternatives)
- `phrase:2` (weight 2)
- `alt1|alt2:1.5` (alts with weight)

**Example:**
```
plants:2; sunlight|solar energy; carbon dioxide:2; water; food
```

## 🧠 Scoring
- The app normalizes text (lowercase, strip punctuation, collapse spaces)
- It searches each keyword/spec via word-boundary-aware regex (works with multi-word phrases)
- Score = (matched_weight / total_weight) × marks_per_question

## 📦 Project Structure
```
keyword_quiz_ml_project/
├── app.py
├── model.py
├── requirements.txt
├── data/
│   └── questions.csv
└── results/
```

## 🚀 Next steps (optional)
- Add stemming/lemmatization and stopword handling
- Show which keywords matched in the UI per question
- Add time limits, categories, difficulty
- Replace keywords with semantic similarity later
