import os
import streamlit as st

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_ollama import ChatOllama
from langchain.schema.runnable import RunnableLambda
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# -----------------------------
# Config
# -----------------------------
MODEL_NAME = "llama2"  # ensure `ollama pull llama2` has been run
TEMPERATURE = 0.3

STYLE_PRESETS = {
    "Polite": "polite, respectful, warm, and courteous; avoid slang; keep it professional.",
    "Friendly": "friendly, upbeat, approachable; conversational tone; light warmth but still professional.",
    "Concise": "very concise, to-the-point, minimal fluff; prioritize clarity and brevity.",
    "Formal": "formal, professional, and businesslike; precise language and proper salutations.",
    "Apologetic": "empathetic and apologetic while taking responsibility and proposing next steps.",
}

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Email Rewriter (LangChain + Ollama)", page_icon="✉️", layout="centered")
st.title("✉️ Email Rewriter")
st.caption("LangChain + Ollama (Llama2) + Streamlit")

with st.sidebar:
    st.subheader("Model")
    model_name = st.text_input("Ollama model", MODEL_NAME, help="Must be available in Ollama, e.g., llama2, llama3, llama3.1")
    temperature = st.slider("Temperature", 0.0, 1.0, TEMPERATURE, 0.1)
    st.markdown("Run `ollama pull llama2` first if needed.")

# Inputs
col1, col2 = st.columns([1, 1])
with col1:
    style_label = st.selectbox("Style preset", list(STYLE_PRESETS.keys()), index=0)
with col2:
    custom_subject = st.text_input("Subject (optional)", "")

original_email = st.text_area(
    "Paste the original email",
    height=220,
    placeholder="Paste the email you want rewritten here..."
)

extra_instructions = st.text_area(
    "Extra constraints (optional)",
    placeholder="e.g., keep under 150 words, include a clear CTA, remove jargon"
)

# -----------------------------
# LangChain: chat model via Ollama
# -----------------------------
@st.cache_resource(show_spinner=False)
def get_llm(name: str, temperature: float):
    # ChatOllama integrates Ollama chat models with LangChain
    return ChatOllama(model=name, temperature=temperature)  # supports streaming via .stream()[12][15]

llm = get_llm(model_name, temperature)

# Prompt: system defines persona and guardrails; human provides inputs
system_template = """You are an expert email editor that rewrites emails in a specified style while preserving core meaning and facts.
Follow the style guidelines strictly and keep the rewritten email practical and ready-to-send.
When appropriate, improve clarity, structure, and tone. Do not invent new facts or promises.

Output only the email body, unless a subject is provided; then include a 'Subject:' line first, followed by a blank line and the body."""

human_template = """Rewrite the following email:

--- Original Email ---
{original_email}
----------------------

Style requirements: {style_requirements}
Subject (optional): {subject_line}
Extra constraints: {constraints}
"""

system_prompt = SystemMessagePromptTemplate.from_template(system_template)
human_prompt = HumanMessagePromptTemplate.from_template(human_template)

prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])  # Llama2 chat prompt formatting handled by LangChain wrappers[6][17]

# -----------------------------
# Chat history (optional to show messages)
# -----------------------------
history = StreamlitChatMessageHistory(key="chat_messages")  # uses Streamlit session state[13]
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    history.add_ai_message("Provide an email and choose a style; I’ll rewrite it.")

for m in history.messages:
    with st.chat_message("assistant" if m.type == "ai" else "user"):
        st.markdown(m.content)

# -----------------------------
# Actions
# -----------------------------
colA, colB = st.columns([1, 1])
run = colA.button("Rewrite")
clear = colB.button("Clear")

if clear:
    st.session_state.pop("chat_messages", None)
    st.rerun()

def build_inputs():
    return {
        "original_email": original_email.strip(),
        "style_requirements": STYLE_PRESETS[style_label],
        "subject_line": (custom_subject or "").strip(),
        "constraints": (extra_instructions or "None").strip(),
    }

def validate():
    if not original_email.strip():
        st.warning("Please paste the original email.")
        return False
    return True

# Streaming output helper
def stream_response(chain_inputs):
    # LCEL-style: prompt | llm
    chain = prompt | llm
    # Stream tokens to UI
    response_container = st.chat_message("assistant")
    placeholder = response_container.empty()
    partial = ""
    for chunk in chain.stream(chain_inputs):  # ChatOllama supports streaming chunks[12]
        partial += chunk.content or ""
        placeholder.markdown(partial)
    return partial

if run:
    if validate():
        user_show = f"Style: {style_label}\n\nOriginal:\n{original_email[:500]}{'...' if len(original_email) > 500 else ''}"
        with st.chat_message("user"):
            st.markdown(user_show)
        history.add_user_message(user_show)

        inputs = build_inputs()
        with st.spinner("Rewriting with Llama2..."):
            out_text = stream_response(inputs)

        history.add_ai_message(out_text)
