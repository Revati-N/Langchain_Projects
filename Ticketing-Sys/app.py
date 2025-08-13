import json
import time
import pandas as pd
import streamlit as st
import ollama

MODEL_NAME = "llama2"  # or a specific tag like "llama2:latest"

CATEGORIES = [
    "PRODUCT_BUG",
    "ACCOUNT_ACCESS",
    "BILLING",
    "FEATURE_REQUEST",
    "USAGE_QUESTION",
    "OTHER",
]

SYSTEM_PROMPT = f"""
You are a strict ticket classifier for customer support.
Pick EXACTLY ONE category from this list:
{", ".join(CATEGORIES)}.

Rules:
- Return ONLY valid JSON with this schema:
  {{"category": "<ONE_LABEL>"}}
- Do not include explanations or extra keys.
- If unsure, use "OTHER".
"""

def classify_text(text: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Ticket:\n{text}\n\nReturn JSON only.",
        },
    ]
    # Call Ollama chat API via Python library
    # Ensure ollama is running locally and model is pulled: `ollama pull llama2`
    resp = ollama.chat(model=MODEL_NAME, messages=messages)  # requires `pip install ollama`
    content = resp.message["content"] if isinstance(resp.message, dict) else resp["message"]["content"]
    # Try to parse JSON from the model output
    try:
        data = json.loads(content.strip())
        category = data.get("category", "OTHER")
        if category not in CATEGORIES:
            category = "OTHER"
        return category
    except Exception:
        # Fallback: attempt to heuristically find a label token
        for cat in CATEGORIES:
            if cat in content:
                return cat
        return "OTHER"

st.set_page_config(page_title="Ticket Classifier (Ollama + Llama2)", page_icon="🎫", layout="centered")

st.title("🎫 Ticket Classifier (Ollama + Llama2)")
st.caption("Runs locally with Ollama. Make sure `ollama serve` is running and Llama 2 is pulled.")

with st.sidebar:
    st.subheader("Model")
    model_name = st.text_input("Ollama model", value=MODEL_NAME, help="e.g., llama2, llama2:latest, llama2:13b (requires sufficient VRAM)")
    if model_name:
        MODEL_NAME = model_name
    st.markdown("Available models (requires running Ollama):")
    try:
        models = [m["model"] for m in ollama.list().get("models", [])]
        st.code("\n".join(models) or "(no models listed)")
    except Exception as e:
        st.warning(f"Could not list models: {e}")

tab_single, tab_batch = st.tabs(["Single ticket", "Batch (CSV)"])

with tab_single:
    st.subheader("Classify a single ticket")
    subject = st.text_input("Subject", "")
    body = st.text_area("Description", "", height=180)
    if st.button("Classify"):
        text = subject.strip() + "\n\n" + body.strip()
        if not text.strip():
            st.warning("Enter subject and/or description.")
        else:
            with st.spinner("Classifying..."):
                t0 = time.time()
                label = classify_text(text)
                dt = time.time() - t0
            st.success(f"Category: {label}  •  {dt:.2f}s")

with tab_batch:
    st.subheader("Batch classify from CSV")
    st.write("Upload a CSV with columns like subject, description.")
    file = st.file_uploader("CSV file", type=["csv"])
    subject_col = st.text_input("Subject column name", value="subject")
    body_col = st.text_input("Description column name", value="description")
    if file and st.button("Run batch"):
        df = pd.read_csv(file)
        if subject_col not in df.columns or body_col not in df.columns:
            st.error(f"CSV must contain '{subject_col}' and '{body_col}'.")
        else:
            results = []
            prog = st.progress(0)
            for i, row in df.iterrows():
                text = f"{row.get(subject_col, '')}\n\n{row.get(body_col, '')}"
                label = classify_text(text)
                results.append(label)
                if (i + 1) % max(1, len(df)//100 or 1) == 0:
                    prog.progress(min(1.0, (i + 1) / len(df)))
            df["predicted_category"] = results
            st.dataframe(df.head(20))
            st.download_button("Download results CSV", df.to_csv(index=False), "classified_tickets.csv", "text/csv")
