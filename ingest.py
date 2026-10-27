from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from constants import DOCUMENTS_DIR, CHROMA_DIR, COLLECTION_NAME, GEMINI_EMBEDDING_MODEL
import hashlib


class RagSystemIngest:
    def __init__(self):
        load_dotenv()
        self.loader = PyPDFDirectoryLoader(str(DOCUMENTS_DIR))
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.embeddings = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
        self.db = Chroma(persist_directory=CHROMA_DIR, embedding_function=self.embeddings, collection_name=COLLECTION_NAME)

    def load_documents(self):
        documents = self.loader.load()
        return documents

    def split_text(self, documents):
        chunks = self.text_splitter.split_documents(documents)
        chunks = [chunk for chunk in chunks if chunk.page_content.strip()]
        return chunks

    def store_embeddings(self, documents):
        ids = []

        for doc in documents:
            source = str(doc.metadata.get("source", ""))
            page = str(doc.metadata.get("page", ""))
            content_hash = hashlib.sha256(
                doc.page_content.encode("utf-8")
            ).hexdigest()

            chunk_id = hashlib.sha256(
                f"{source}|{page}|{content_hash}".encode("utf-8")
            ).hexdigest()

            ids.append(chunk_id)

        if documents:
            self.db.add_documents(
                documents=documents,
                ids=ids,
            )
            
    def ingest(self):
        documents = self.load_documents()
        chunks = self.split_text(documents)
        self.store_embeddings(chunks)