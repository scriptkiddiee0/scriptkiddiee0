import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import json
import tempfile
from datetime import datetime
import io

try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False

from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.set_page_config(
    page_title="CareBot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d0f14;
        color: #d4cfc7;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] { background-color: #0d0f14; }

    h1 {
        font-family: 'DM Serif Display', serif;
        color: #e8e2d9 !important;
        letter-spacing: 0.02em;
    }

    [data-testid="stChatMessage"] {
        background: #13161d;
        border: 1px solid #1e2330;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }

    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }

    .custom-input-row {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: #0d0f14;
        padding: 14px 2rem 18px 2rem;
    }
    .custom-input-row .stTextInput input {
        background: #13161d !important;
        color: #d4cfc7 !important;
        border: 1px solid #2a3040 !important;
        border-radius: 14px 0 0 14px !important;
        padding: 12px 18px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        box-shadow: none !important;
        outline: none !important;
        height: 52px !important;
    }
    .custom-input-row .stTextInput input:focus {
        border-color: #4a9eff !important;
        box-shadow: 0 0 0 3px rgba(74,158,255,0.12) !important;
    }
    .custom-input-row .stTextInput input::placeholder {
        color: #3a4055 !important;
    }
    .custom-input-row .send-btn .stButton > button {
        background: #1a2a3a !important;
        color: #4a9eff !important;
        border: 1px solid #2a3040 !important;
        border-left: none !important;
        border-radius: 0 14px 14px 0 !important;
        height: 52px !important;
        padding: 0 18px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: background 0.18s ease !important;
    }
    .custom-input-row .send-btn .stButton > button:hover {
        background: #1e3a50 !important;
        color: #6ab4ff !important;
    }
    .custom-input-row .mic-btn .stButton > button {
        background: #13161d !important;
        color: #3a5070 !important;
        border: 1px solid #2a3040 !important;
        border-left: none !important;
        border-radius: 0 !important;
        height: 52px !important;
        padding: 0 14px !important;
        font-size: 1rem !important;
        transition: all 0.18s ease !important;
    }
    .custom-input-row .mic-btn .stButton > button:hover {
        color: #4a9eff !important;
        background: #161b26 !important;
    }
    .custom-input-row .mic-btn-active .stButton > button {
        color: #4a9eff !important;
        background: #0f1a28 !important;
    }
    .block-container {
        padding-bottom: 90px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0f1118;
        border-right: 1px solid #1a1e2a;
    }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #0d0f14; }
    ::-webkit-scrollbar-thumb { background: #222536; border-radius: 4px; }

    .stButton > button {
        background-color: #13161d;
        color: #7a9abb;
        border: 1px solid #1e2a38;
        border-radius: 6px;
        font-size: 0.78rem;
        padding: 7px 14px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        letter-spacing: 0.02em;
        transition: all 0.18s ease;
    }
    .stButton > button:hover {
        background-color: #161b26;
        border-color: #2e4a6a;
        color: #b0c8e0;
    }

    [data-testid="metric-container"] {
        background: #13161d;
        border: 1px solid #1e2330;
        border-radius: 8px;
        padding: 10px;
    }

    [data-testid="stFileUploader"] {
        background: #13161d;
        border: 1px dashed #1e2a38;
        border-radius: 8px;
        padding: 12px;
    }

    [data-testid="stAlert"] {
        background: #111520 !important;
        border: 1px solid #1e2a38 !important;
        border-radius: 8px !important;
        color: #7a9abb !important;
    }

    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

USER_AVATAR_HTML = """
<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <div style="width:28px;height:28px;border-radius:50%;background:#161b26;
        border:1px solid #2a3040;display:flex;align-items:center;justify-content:center;
        font-size:12px;flex-shrink:0;box-shadow:0 0 8px rgba(100,120,200,0.18);">👤</div>
    <span style="font-size:0.7rem;color:#4a5570;letter-spacing:0.1em;text-transform:uppercase;font-family:'Inter',sans-serif;font-weight:600;">You</span>
</div>
"""

BOT_AVATAR_HTML = """
<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <div style="width:28px;height:28px;border-radius:50%;background:#0f1a28;
        border:1px solid #2a4060;display:flex;align-items:center;justify-content:center;
        font-size:12px;flex-shrink:0;box-shadow:0 0 10px rgba(40,100,180,0.25);">+</div>
    <span style="font-size:0.7rem;color:#2e5070;letter-spacing:0.1em;text-transform:uppercase;font-family:'Inter',sans-serif;font-weight:600;">CareBot</span>
</div>
"""

CHROMA_PERSIST_DIR = "chroma_db"
CHROMA_COLLECTION_NAME = "chatbot"
DATA_PATH = "data"

CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say that you don't know — don't try to make up an answer.
Don't provide anything outside the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""

QUICK_SUGGESTIONS = [
    ("Symptoms", "What are common symptoms of diabetes?"),
    ("Blood Pressure", "How to manage high blood pressure?"),
    ("Fatigue", "What causes persistent fatigue?"),
    ("Mental Health", "What are early signs of anxiety?"),
]


def load_documents(data_dir: str = DATA_PATH):
    data_path = Path(data_dir)
    if not data_path.exists():
        raise RuntimeError(f"Data directory not found at '{data_dir}'.")
    documents = []
    for path in sorted(data_path.rglob("*.txt")):
        documents.extend(TextLoader(str(path)).load())
    for path in sorted(data_path.rglob("*.pdf")):
        documents.extend(PyPDFLoader(str(path)).load())
    if not documents:
        raise RuntimeError(f"No documents found in '{data_dir}'.")
    return documents


@st.cache_resource
def build_vectorstore(source_docs=None):
    if source_docs is None:
        source_docs = load_documents()
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma.from_documents(
        source_docs, embedding_model,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
    )


@st.cache_resource
def get_vectorstore():
    if not os.path.exists(CHROMA_PERSIST_DIR):
        return build_vectorstore()
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=CHROMA_PERSIST_DIR,
    )


def set_custom_prompt(template):
    return PromptTemplate(template=template, input_variables=["context", "question"])


def build_qa_chain(vectorstore):
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0.0,
        max_tokens=None, timeout=None, max_retries=2, api_key=gemini_api_key,
    )
    return RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)},
    )


def build_qa_chain_with_custom_store(vectorstore):
    return build_qa_chain(vectorstore)


def format_source_documents(source_documents):
    if not source_documents:
        return ""
    lines = []
    for doc in source_documents:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "")
        lines.append(f"- {source} (page {page})" if page else f"- {source}")
    return "\n\n**Sources:**\n" + "\n".join(lines)


def audio_to_text(audio_bytes):
    if not HAS_SPEECH_RECOGNITION:
        st.error("Speech recognition not available.")
        return None
    try:
        recognizer = sr.Recognizer()
        audio_io = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_io) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        st.warning("Could not understand audio. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return None


def render_message(role: str, content: str):
    avatar_html = USER_AVATAR_HTML if role == "User" else BOT_AVATAR_HTML
    with st.chat_message(role):
        st.markdown(avatar_html, unsafe_allow_html=True)
        st.markdown(content)


def get_answer(prompt, use_uploaded_files, temp_vectorstore):
    if use_uploaded_files and temp_vectorstore:
        qa_chain = build_qa_chain_with_custom_store(temp_vectorstore)
        response = qa_chain.invoke({"query": prompt})
        result = response.get("result") or response.get("output_text") or ""
        sources = format_source_documents(response.get("source_documents", []))
        return result + sources
    elif temp_vectorstore:
        qa_temp = build_qa_chain_with_custom_store(temp_vectorstore)
        r_temp = qa_temp.invoke({"query": prompt})
        qa_base = build_qa_chain(get_vectorstore())
        r_base = qa_base.invoke({"query": prompt})
        result = (
            f"**From Uploaded Documents:**\n{r_temp.get('result','')}\n\n"
            f"**From Base Knowledge:**\n{r_base.get('result','')}"
        )
        all_docs = r_temp.get("source_documents", []) + r_base.get("source_documents", [])
        return result + format_source_documents(all_docs)
    else:
        qa_chain = build_qa_chain(get_vectorstore())
        response = qa_chain.invoke({"query": prompt})
        result = response.get("result") or response.get("output_text") or ""
        sources = format_source_documents(response.get("source_documents", []))
        return result + sources


# ── Callback: captures typed text before the widget resets ───────────────────
def _submit_input():
    """Called by on_change when Enter is pressed or send is clicked."""
    val = st.session_state.get("chat_text_input", "").strip()
    if val:
        st.session_state.pending_prompt = val
    # clear the widget immediately via its own key (safe inside a callback)
    st.session_state["chat_text_input"] = ""


def main():
    # ── Session state init ────────────────────────────────────────────────────
    for key, default in [
        ("messages", []),
        ("suggested_prompt", None),
        ("total_questions", 0),
        ("show_voice", False),
        ("pending_prompt", None),   # ← holds the submitted text between reruns
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 20px 4px 12px 4px;">
                <div style="font-family:'DM Serif Display',serif;font-size:1.35rem;color:#c8c2b8;
                    letter-spacing:0.04em;">CareBot</div>
                <div style="height:1px;background:#1a1e2a;margin-top:10px;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("New Chat", use_container_width=True, key="new_chat_btn"):
            st.session_state.messages = []
            st.session_state.total_questions = 0
            st.session_state.pending_prompt = None
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="font-size:0.7rem;color:#3a4055;letter-spacing:0.1em;
                text-transform:uppercase;margin-top:16px;margin-bottom:8px;
                font-family:'Inter',sans-serif;font-weight:600;">Upload Report</div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("PDF or TXT files — your documents stay private")

        uploaded_files = st.file_uploader(
            "Choose files", type=["pdf", "txt"],
            accept_multiple_files=True, label_visibility="collapsed",
        )

        use_uploaded_files = False
        temp_vectorstore = None

        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) ready")
            with st.spinner("Processing..."):
                temp_docs = []
                temp_dir = tempfile.mkdtemp()
                for f in uploaded_files:
                    fpath = os.path.join(temp_dir, f.name)
                    with open(fpath, "wb") as out:
                        out.write(f.getbuffer())
                    try:
                        if f.name.endswith(".pdf"):
                            temp_docs.extend(PyPDFLoader(fpath).load())
                        elif f.name.endswith(".txt"):
                            temp_docs.extend(TextLoader(fpath).load())
                    except Exception as e:
                        st.warning(f"Could not read {f.name}: {e}")

                if temp_docs:
                    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                    temp_vectorstore = Chroma.from_documents(temp_docs, emb, collection_name="temp_uploads")
                    use_uploaded_files = st.checkbox(
                        "Answer from uploaded docs only",
                        value=False,
                    )

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='height:1px;background:#1a1e2a;margin-bottom:12px;'></div>",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        col_a.metric("Questions", st.session_state.total_questions)
        col_b.metric("Messages", len(st.session_state.messages))

        if st.session_state.messages:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            chat_data = {
                "exported_at": datetime.now().isoformat(),
                "total_questions": st.session_state.total_questions,
                "messages": st.session_state.messages,
            }
            st.download_button(
                label="Export chat",
                data=json.dumps(chat_data, indent=2),
                file_name=f"carebot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="download_btn",
            )

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="height:1px;background:#1a1e2a;margin-bottom:16px;"></div>
            <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:16px;">
                <div style="display:flex;align-items:center;gap:9px;">
                    <div style="width:15px;height:15px;border:1.5px solid #2a4a2a;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                        <div style="width:6px;height:4px;border-left:1.5px solid #3a7a3a;
                            border-bottom:1.5px solid #3a7a3a;transform:rotate(-45deg);margin-top:-1px;"></div>
                    </div>
                    <span style="font-size:0.74rem;color:#3a5040;font-family:'Inter',sans-serif;">Evidence-based information</span>
                </div>
                <div style="display:flex;align-items:center;gap:9px;">
                    <div style="width:15px;height:15px;border:1.5px solid #2a4a2a;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                        <div style="width:6px;height:4px;border-left:1.5px solid #3a7a3a;
                            border-bottom:1.5px solid #3a7a3a;transform:rotate(-45deg);margin-top:-1px;"></div>
                    </div>
                    <span style="font-size:0.74rem;color:#3a5040;font-family:'Inter',sans-serif;">Private document analysis</span>
                </div>
                <div style="display:flex;align-items:center;gap:9px;">
                    <div style="width:15px;height:15px;border:1.5px solid #2a3a4a;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                        <div style="width:5px;height:5px;border:1.5px solid #3a5a7a;border-radius:50%;"></div>
                    </div>
                    <span style="font-size:0.74rem;color:#2e3d4a;font-family:'Inter',sans-serif;">Not a replacement for professional care</span>
                </div>
            </div>
            <div style="font-size:0.65rem;color:#222630;line-height:1.6;font-family:'Inter',sans-serif;padding:0 2px;">
                For informational use only. Not a substitute for professional medical advice.
            </div>
            """,
            unsafe_allow_html=True,
        )

    has_messages = bool(st.session_state.messages)

    # ── Main area header — only shown on empty chat ───────────────────────────
    if not has_messages:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:22px;margin-bottom:4px;margin-top:8px;">
                <div style="flex-shrink:0;">
                    <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
                        <line x1="36" y1="6" x2="36" y2="16" stroke="#3a6090" stroke-width="2.5" stroke-linecap="round"/>
                        <circle cx="36" cy="4.5" r="3" fill="#4a80b0" opacity="0.9"/>
                        <rect x="16" y="16" width="40" height="30" rx="9" fill="#13161d" stroke="#2a4060" stroke-width="1.8"/>
                        <rect x="22" y="24" width="10" height="7" rx="3" fill="#1a3a5c"/>
                        <rect x="40" y="24" width="10" height="7" rx="3" fill="#1a3a5c"/>
                        <circle cx="27" cy="27.5" r="2.5" fill="#4a9eff" opacity="0.95"/>
                        <circle cx="45" cy="27.5" r="2.5" fill="#4a9eff" opacity="0.95"/>
                        <rect x="25" y="36" width="22" height="5" rx="2.5" fill="#1a3a5c"/>
                        <rect x="27" y="37.5" width="4" height="2" rx="1" fill="#4a9eff" opacity="0.8"/>
                        <rect x="33" y="37.5" width="4" height="2" rx="1" fill="#4a9eff" opacity="0.8"/>
                        <rect x="39" y="37.5" width="4" height="2" rx="1" fill="#4a9eff" opacity="0.8"/>
                        <rect x="8" y="22" width="8" height="14" rx="4" fill="#13161d" stroke="#2a4060" stroke-width="1.5"/>
                        <rect x="56" y="22" width="8" height="14" rx="4" fill="#13161d" stroke="#2a4060" stroke-width="1.5"/>
                        <rect x="20" y="48" width="32" height="18" rx="6" fill="#13161d" stroke="#2a4060" stroke-width="1.8"/>
                        <rect x="33" y="52" width="6" height="10" rx="1.5" fill="#2a5080" opacity="0.9"/>
                        <rect x="30" y="55" width="12" height="4" rx="1.5" fill="#2a5080" opacity="0.9"/>
                        <rect x="22" y="66" width="10" height="5" rx="2.5" fill="#13161d" stroke="#2a4060" stroke-width="1.5"/>
                        <rect x="40" y="66" width="10" height="5" rx="2.5" fill="#13161d" stroke="#2a4060" stroke-width="1.5"/>
                    </svg>
                </div>
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:2.6rem;line-height:1.1;
                        color:#e8e2d9;letter-spacing:0.04em;">ASK CAREBOT</div>
                    <div style="font-family:'DM Mono',monospace;font-size:0.78rem;color:#3a6090;
                        letter-spacing:0.18em;text-transform:uppercase;margin-top:5px;">
                        YOUR PERSONAL AI HEALTH ASSISTANT</div>
                </div>
            </div>
            <div style="height:1px;background:linear-gradient(90deg,#2a4060 0%,transparent 80%);margin-bottom:28px;"></div>
            """,
            unsafe_allow_html=True,
        )

    if use_uploaded_files and temp_vectorstore:
        st.info("Answering from your uploaded documents only.")
    elif temp_vectorstore:
        st.info("Searching both uploaded documents and base knowledge.")

    # ── Quick Suggestion Cards — only on empty chat ───────────────────────────
    if not has_messages:
        st.markdown(
            "<div style='font-size:0.7rem;color:#4a9eff;text-shadow:0 0 8px rgba(74,158,255,0.5);letter-spacing:0.1em;text-transform:uppercase;"
            "margin-bottom:14px;font-family:\"Inter\",sans-serif;font-weight:600;'>Common Questions</div>",
            unsafe_allow_html=True,
        )

        cols = st.columns(4)
        card_css = """
            background:#111520;
            border:1px solid #1a2030;
            border-radius:16px;
            padding:20px 16px;
            cursor:pointer;
            transition:border-color 0.18s ease, background 0.18s ease;
            min-height:90px;
            display:flex;
            flex-direction:column;
            justify-content:flex-end;
        """

        for i, (label, question) in enumerate(QUICK_SUGGESTIONS):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="{card_css}">
                        <div style="font-size:0.68rem;color:#2e3a4a;text-transform:uppercase;
                            letter-spacing:0.1em;font-family:'Inter',sans-serif;font-weight:600;
                            margin-bottom:6px;">{label}</div>
                        <div style="font-size:0.82rem;color:#7a8a9a;font-family:'Inter',sans-serif;
                            line-height:1.4;">{question}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Ask", key=f"sug_{i}", use_container_width=True):
                    st.session_state.pending_prompt = question
                    st.rerun()

        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    # ── Conversation history ──────────────────────────────────────────────────
    for message in st.session_state.messages:
        render_message(message["role"], message["content"])

    # Scroll anchor — keeps the latest message above the fixed input bar
    st.markdown('<div id="chat-bottom"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <script>
            const el = document.getElementById('chat-bottom');
            if (el) el.scrollIntoView({ behavior: 'smooth' });
        </script>
        """,
        unsafe_allow_html=True,
    )

    # ── Fixed input bar ───────────────────────────────────────────────────────
    st.markdown('<div class="custom-input-row">', unsafe_allow_html=True)

    if HAS_SPEECH_RECOGNITION:
        col_text, col_mic, col_send = st.columns([11, 1, 1])
    else:
        col_text, col_send = st.columns([12, 1])
        col_mic = None

    with col_text:
        # on_change fires BEFORE the rerun, capturing text into pending_prompt
        st.text_input(
            "input",
            label_visibility="collapsed",
            placeholder="Ask a health question...",
            key="chat_text_input",
            on_change=_submit_input,
        )

    if col_mic:
        mic_class = "mic-btn-active" if st.session_state.show_voice else "mic-btn"
        st.markdown(f'<div class="{mic_class}">', unsafe_allow_html=True)
        with col_mic:
            if st.button("🎙", key="mic_toggle"):
                st.session_state.show_voice = not st.session_state.show_voice
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="send-btn">', unsafe_allow_html=True)
    with col_send:
        # Send button also calls the same callback to grab whatever is in the field
        if st.button("↑", key="send_btn", on_click=_submit_input):
            pass   # logic handled inside _submit_input + pending_prompt below
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Voice input ───────────────────────────────────────────────────────────
    if HAS_SPEECH_RECOGNITION and st.session_state.show_voice:
        audio_data = st.audio_input("Speak now", label_visibility="visible")
        if audio_data:
            with st.spinner("Converting speech to text..."):
                voice_prompt = audio_to_text(audio_data.getvalue())
                if voice_prompt:
                    st.success(f"Heard: **{voice_prompt}**")
                    st.session_state.pending_prompt = voice_prompt
                    st.session_state.show_voice = False

    # ── Resolve the final prompt from all sources ─────────────────────────────
    prompt = None
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None   # consume it

    # ── Process the prompt ────────────────────────────────────────────────────
    if prompt:
        # Append user message first so sidebar counters update on this rerun
        st.session_state.messages.append({"role": "User", "content": prompt})
        st.session_state.total_questions += 1

        render_message("User", prompt)

        with st.spinner("CareBot is thinking..."):
            try:
                answer = get_answer(prompt, use_uploaded_files, temp_vectorstore)
            except Exception as e:
                answer = f"Something went wrong: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        render_message("assistant", answer)
        st.rerun()


if __name__ == "__main__":
    main()
