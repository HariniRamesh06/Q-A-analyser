# app.py
import streamlit as st
import pandas as pd
from model import KeywordMatcher, parse_keywords_field
import platform
from PIL import Image
import pytesseract
import os

# Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# TESSDATA_PREFIX should point to the tessdata folder
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Try importing OCR
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Configure Tesseract path on Windows
if platform.system() == "Windows" and OCR_AVAILABLE:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # adjust if needed

st.set_page_config(page_title="Keyword-Based Quiz (ML-style)", page_icon="🧠", layout="centered")

st.title("🧠 Keyword-Based Quiz (ML-style)")
st.write("Type your answer for each question or upload a handwritten answer. "
         "Scoring is based on **keyword/phrase matches**, with optional **weights** and **synonyms**.")

@st.cache_data
def load_questions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"question", "keywords"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")
    return df

df = load_questions("data/questions.csv")
marks_per_question = st.sidebar.number_input("Marks per question", min_value=1, max_value=20, value=10)
matcher = KeywordMatcher(marks_per_question=marks_per_question)

if 'current' not in st.session_state:
    st.session_state.current = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []

total_questions = len(df)

def reset_quiz():
    st.session_state.current = 0
    st.session_state.answers = []

st.sidebar.button("🔁 Restart quiz", on_click=reset_quiz)

# ----------------- Quiz Question Block -----------------
if st.session_state.current < total_questions:
    row = df.iloc[st.session_state.current]
    st.subheader(f"Q{st.session_state.current+1}. {row['question']}")

    with st.expander("🔍 View expected keywords format (optional)", expanded=False):
        st.markdown("""
        - Separate keyword specs with `;`  
        - Use `|` to list synonyms/alternatives for the same concept  
        - Add `:weight` to adjust importance  
        **Example:** `plants:2; sunlight|solar energy; carbon dioxide:2; water; food`
        """)
        st.code(row["keywords"])

    # --- OCR / input mode ---
    mode = st.radio("Answer mode", ["Type answer", "Upload image (OCR)"], horizontal=True)

    extracted_text = ""
    if mode == "Upload image (OCR)" and OCR_AVAILABLE:
        uploaded_image = st.file_uploader("Upload your handwritten answer (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            img = Image.open(uploaded_image).convert("RGB")
            extracted_text = pytesseract.image_to_string(img)
            if extracted_text.strip():
                st.success("OCR text extracted. You can edit it below.")
            else:
                st.warning("No text detected. You can type your answer manually.")

    # Text area for typing or editing OCR output
    user_ans = st.text_area("Your answer",
                            value=extracted_text if extracted_text else "",
                            height=150,
                            key=f"ans_{st.session_state.current}")

    # Submit / skip buttons
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.button("Submit answer ➡️")
    with col2:
        skipped = st.button("Skip ➡️")

    if submitted or skipped:
        final_text = user_ans if submitted else ""
        result = matcher.score(final_text, row["keywords"]) if submitted else matcher.score("", row["keywords"])

        st.session_state.answers.append({
            "question": row["question"],
            "keywords": row["keywords"],
            "your_answer": final_text,
            **result
        })
        st.session_state.current += 1
        st.rerun()

# ----------------- Quiz Results Block -----------------
else:
    st.success("🎉 Quiz complete! Here's your performance breakdown:")
    results_df = pd.DataFrame(st.session_state.answers)
    total_score = results_df["score"].sum()
    max_score = marks_per_question * total_questions
    overall_pct = (total_score / max_score) * 100 if max_score else 0

    st.metric("Final Score", f"{total_score:.2f} / {max_score:.2f}")
    st.metric("Overall Percentage", f"{overall_pct:.2f}%")

    with st.expander("📋 Detailed per-question results", expanded=True):
        show_cols = ["question", "your_answer", "score", "percentage_for_question",
                     "matched_unweighted", "total_keywords", "matched_weight", "total_weight", "keywords"]
        st.dataframe(results_df[show_cols], use_container_width=True)

    # Save results
    import os, datetime
    os.makedirs("results", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"results/quiz_results_{ts}.csv"
    results_df.to_csv(out_path, index=False)

    with open(out_path, "rb") as f:
        st.download_button(label="⬇️ Download results CSV", data=f,
                           file_name=f"quiz_results_{ts}.csv", mime="text/csv")

    st.info("Tip: You can edit `data/questions.csv` to add or modify questions and keyword specs, then restart the quiz from the sidebar.")
