# Keyword-Based Quiz (ML-style)

This project is a lightweight, **ML-style** quiz app that scores free-text answers using **keyword/phrase matching** with **synonyms** and **weights**. It uses Streamlit for the UI.

## ✨ Features
- Semicolon-separated keyword specs per question
- Synonyms/alternatives with `|`
- Optional weights with `:number`
- Per-question score and overall percentage
- Downloadable results CSV
- Easy to extend/reuse

## 🔧 Install & Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

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
