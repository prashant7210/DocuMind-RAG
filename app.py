from pathlib import Path
import streamlit as st
from constants import DOCUMENTS_DIR
from ingest import RagSystemIngest
from rag import RagSystem
import re


def get_common_response(query: str) -> str | None:
    """Handle common conversational inputs without RAG retrieval."""

    normalized = re.sub(
        r"[^\w\s]",
        "",
        query.lower()
    ).strip()

    # Exact matches prevent ordinary document questions
    # from accidentally being classified as greetings.
    responses = {
        "hi": "Hello! How can I help you explore your documents today?",
        "hello": "Hello! How can I help you explore your documents today?",
        "hey": "Hey! What would you like to know from your documents?",

        "good morning": "Good morning! What would you like to know from your documents?",
        "good afternoon": "Good afternoon! How can I help you today?",
        "good evening": "Good evening! What can I help you find?",

        "how are you": "I'm doing well, thanks for asking! What can I help you find?",
        "thanks": "You're welcome! Feel free to ask another question.",
        "thank you": "You're welcome! Feel free to ask another question.",
        "thank you so much": "You're very welcome! Let me know if you need anything else.",

        "bye": "Goodbye! Come back whenever you need help with your documents.",
        "goodbye": "Goodbye! Have a great day.",
        "see you": "See you next time! I'll be here when you need help with your documents.",

        "who are you": (
            "I'm your Knowledge Assistant. I answer questions "
            "using your uploaded and indexed documents."
        ),

        "what can you do": (
            "I can search your uploaded documents, answer questions "
            "based on their content, and show relevant source pages."
        ),

        "how does this work": (
            "I retrieve relevant passages from your documents and "
            "use them to generate an answer grounded in that context."
        ),

        "what can i ask": (
            "Ask about definitions, requirements, procedures, policies, "
            "or findings covered in your uploaded PDFs."
        ),

        "how do i upload a document": (
            "Use the Upload PDF section in the sidebar, select your "
            "files, and click Upload and index."
        ),

        "where do your answers come from": (
            "My answers are based on passages retrieved from your "
            "indexed documents. I can show source filenames and "
            "page numbers when available."
        ),

        "can you answer anything": (
            "I focus on your uploaded documents. If they don't contain "
            "enough information, I'll tell you rather than inventing an answer."
        ),
    }

    return responses.get(normalized)


def has_sufficient_information(answer: str) -> bool:
    """Check whether the RAG answer indicates missing information."""

    unavailable_phrases = [
        "the available documents do not provide enough information",
        "the documents do not contain enough information",
        "the context does not contain enough information",
        "i cannot answer based on the provided context",
        "the provided context does not contain",
        "no relevant information was found",
    ]

    normalized_answer = answer.strip().lower()

    return not any(
        phrase in normalized_answer
        for phrase in unavailable_phrases
    )

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
)

DOCUMENTS_PATH = Path(DOCUMENTS_DIR)
DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        color: white;
        background: linear-gradient(120deg, #123047, #176B70);
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 8px;
    }

    .hero p {
        color: #E0F2F1;
        margin-bottom: 0;
    }

    [data-testid="stChatMessage"] {
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Reuse one RAG instance
# --------------------------------------------------
@st.cache_resource
def get_rag():
    return RagSystem()


# --------------------------------------------------
# Session state
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed_hashes" not in st.session_state:
    st.session_state.indexed_hashes = set()


# --------------------------------------------------
# Sidebar: upload and index PDFs
# --------------------------------------------------
with st.sidebar:
    st.title("🧠 Knowledge Assistant")
    st.caption("Search your documents using AI.")

    st.divider()
    st.subheader("Document library")

    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDFs to your knowledge base.",
    )

    if st.button(
        "Upload and index",
        type="primary",
        use_container_width=True,
    ):
        if not uploaded_files:
            st.warning("Select at least one PDF.")
        else:
            saved_files = 0
            skipped_files = 0

            try:
                import hashlib

                for uploaded_file in uploaded_files:
                    file_bytes = uploaded_file.getvalue()
                    digest = hashlib.sha256(file_bytes).hexdigest()

                    if digest in st.session_state.indexed_hashes:
                        skipped_files += 1
                        continue

                    destination = (
                        DOCUMENTS_PATH / Path(uploaded_file.name).name
                    )

                    # Do not overwrite an existing file silently.
                    if destination.exists():
                        existing_digest = hashlib.sha256(
                            destination.read_bytes()
                        ).hexdigest()

                        if existing_digest == digest:
                            st.session_state.indexed_hashes.add(digest)
                            skipped_files += 1
                            continue

                        st.warning(
                            f"{uploaded_file.name} already exists "
                            "with different content. Rename the new file."
                        )
                        skipped_files += 1
                        continue

                    destination.write_bytes(file_bytes)
                    st.session_state.indexed_hashes.add(digest)
                    saved_files += 1

                if saved_files:
                    with st.spinner("Indexing your documents..."):
                        RagSystemIngest().ingest()

                    # Clear the cached RAG instance so the next
                    # interaction initializes against the updated DB.
                    get_rag.clear()

                    st.success(
                        f"Successfully indexed {saved_files} PDF(s)."
                    )

                if skipped_files:
                    st.info(
                        f"Skipped {skipped_files} duplicate or "
                        "conflicting file(s)."
                    )

            except Exception as exc:
                st.error(f"Upload or indexing failed: {exc}")

    st.divider()

    # Show PDFs currently in the document directory.
    pdf_files = sorted(DOCUMENTS_PATH.glob("*.pdf"))

    st.subheader(f"Documents ({len(pdf_files)})")

    if pdf_files:
        for pdf in pdf_files:
            st.caption(f"📄 {pdf.name}")
    else:
        st.caption("No PDFs uploaded yet.")

    st.divider()

    if st.button("Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# Main page
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>Ask your documents.</h1>
        <p>
            Get clear answers grounded in your own PDF knowledge base.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Chat with your knowledge base")
st.caption(
    "Ask questions about your indexed documents. "
    "Answers include the source pages used for retrieval."
)


# --------------------------------------------------
# Display conversation history
# --------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            sources = message.get("sources", [])

            if sources:
                with st.expander("📚 View sources"):
                    seen = set()

                    for source in sources:
                        filename = Path(
                            source.get("source", "Unknown source")
                        ).name

                        page = source.get("page")
                        label = (
                            f"{filename} — Page {page}"
                            if page is not None
                            else filename
                        )

                        if label not in seen:
                            st.markdown(f"- {label}")
                            seen.add(label)


# --------------------------------------------------
# Process user queries
# --------------------------------------------------
question = st.chat_input("Ask a question about your PDFs...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        common_response = get_common_response(question.lower())

        if common_response is not None:
            # Conversational input: no embeddings, retrieval,
            # or Gemini generation required.
            answer = common_response
            sources = []

        else:
            try:
                with st.spinner(
                    "Searching documents and generating an answer..."
                ):
                    rag = get_rag()
                    result = rag.answer_with_sources(question)

                    answer = result["answer"]
                    sources = result["sources"]

            except Exception as exc:
                st.error(f"Unable to process your question: {exc}")
                answer = None
                sources = []

        if answer is not None:
            st.markdown(answer)

            # Keep your existing information-availability
            # check here if you have implemented it.
            if (
                sources
                and get_common_response(question) is None
                and has_sufficient_information(answer)
            ):
                with st.expander("📚 View sources"):
                    seen = set()

                    for source in sources:
                        filename = Path(
                            source.get("source", "Unknown source")
                        ).name

                        page = source.get("page")
                        label = (
                            f"{filename} — Page {page}"
                            if page is not None
                            else filename
                        )

                        if label not in seen:
                            st.markdown(f"- {label}")
                            seen.add(label)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })