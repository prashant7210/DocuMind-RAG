# DocuMind-RAG 🧠

**An AI-powered document question-answering application built with Retrieval-Augmented Generation (RAG).**

DocuMind-RAG allows users to upload PDF documents, ask questions in a conversational interface, and receive answers grounded in the content of their documents. It combines LangChain, Google Gemini, ChromaDB, and Streamlit to provide an interactive and user-friendly document search experience.

## ✨ Features

- **PDF Document Upload:** Upload one or multiple PDF files through the Streamlit interface.
- **Intelligent Document Processing:** Load, split, and prepare documents for semantic search.
- **Semantic Search:** Retrieve relevant document chunks using vector embeddings and ChromaDB.
- **Context-Grounded Answers:** Generate responses using Google Gemini and retrieved document context.
- **Source References:** Display source filenames and page numbers for retrieved information.
- **Persistent Vector Storage:** Store document embeddings locally using ChromaDB.
- **Automatic Ingestion:** Automatically index documents when the vector database is empty.
- **Conversational Interface:** Interact with your documents through a Streamlit chat interface.
- **Common Query Handling:** Respond to greetings and common conversational inputs without unnecessary document retrieval.
- **Context-Aware Responses:** Indicate when the available documents do not provide sufficient information to answer a question.

## 🏗️ Architecture

DocuMind-RAG consists of two main pipelines.

### 1. Document Ingestion Pipeline

1. Load PDF documents from the configured directory.
2. Split documents into smaller, overlapping text chunks.
3. Generate embeddings using Google Gemini's embedding model.
4. Store document chunks and their embeddings in ChromaDB.

### 2. Question-Answering Pipeline

1. Accept a user's question through the Streamlit interface.
2. Retrieve the most relevant document chunks from ChromaDB.
3. Format the retrieved context and source metadata.
4. Combine the context and question using a structured prompt template.
5. Generate an answer using Google Gemini.
6. Display the answer and relevant source references in the interface.

```text
                 PDF Documents
                       |
                       v
              Document Loader
                       |
                       v
                Text Splitter
                       |
                       v
              Gemini Embeddings
                       |
                       v
                  ChromaDB
                       |
                       |  Semantic Retrieval
                       v
User Query ------> Retrieve Relevant Chunks
                       |
                       v
                Prompt Template
                       |
                       v
                 Gemini LLM
                       |
                       v
              Generated Answer
                       |
                       v
                Streamlit UI
             Answer + Source Pages
```

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Core programming language |
| Streamlit | Interactive web interface |
| LangChain | RAG pipeline and prompt management |
| Google Gemini | Embeddings and answer generation |
| ChromaDB | Vector storage and semantic retrieval |
| PyPDF | PDF document processing |
| python-dotenv | Environment variable management |

## 📁 Project Structure

```text
DocuMind-RAG/
│
├── app.py                  # Streamlit application
├── rag_system.py           # RAG retrieval and generation logic
├── ingest.py               # Document ingestion and indexing
├── constants.py            # Application configuration
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── documents/              # PDF documents
├── chroma_db/              # Persistent vector database
└── README.md
```

*Note: Adjust filenames and directories above to match your actual project structure.*

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.12
- Git
- A Google Gemini API key
- A terminal or IDE such as Visual Studio Code

### 1. Clone the Repository

```bash
git clone https://github.com/prashant7210/DocuMind-RAG.git
cd DocuMind-RAG
```

### 2. Create a Virtual Environment

**Windows:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python directly or use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

Obtain your API key from [Google AI Studio](https://aistudio.google.com/apikey).

Ensure that your application loads the environment variables using `load_dotenv()`.

**Security:** Never commit your `.env` file or expose your API key in source code.

### 5. Prepare the Documents Directory

Create the directory configured by `DOCUMENTS_DIR` in `constants.py`.

```text
documents/
    example.pdf
```

Place your PDF documents in this directory. The application uses the configured directory for ingestion and retrieval.

### 6. Run the Application

From the project root, execute:

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## 💬 Usage

1. Launch the Streamlit application.
2. Upload one or more PDF documents using the sidebar.
3. Click the document indexing button.
4. Wait for the documents to be processed and stored in ChromaDB.
5. Enter a question in the chat input.
6. Read the generated answer.
7. Expand the sources section to inspect the retrieved document filenames and page numbers.

The application retrieves relevant passages and generates an answer based on the available document context.

## 🔐 Security and Data Management

- Store API keys in environment variables.
- Exclude `.env` and `.venv/` from version control.
- Exclude local vector databases and private documents unless you explicitly intend to share them.
- Treat generated answers as potentially imperfect and verify important information against the original documents.

## 🚀 Future Improvements

- Add persistent chat history using SQLite.
- Implement incremental document ingestion and duplicate detection.
- Support additional document formats such as DOCX and TXT.
- Add RAG evaluation using metrics such as faithfulness, answer relevancy, context precision, and context recall.
- Improve retrieval with metadata filtering and reranking.
- Add document management features for removing and updating indexed files.
- Deploy the application to a suitable hosting platform.

**Built with Python, LangChain, Google Gemini, ChromaDB, and Streamlit.**
