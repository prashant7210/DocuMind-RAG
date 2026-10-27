from operator import itemgetter
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from constants import CHROMA_DIR, COLLECTION_NAME, GEMINI_CHAT_MODEL, GEMINI_EMBEDDING_MODEL, TEMPLATE
from ingest import RagSystemIngest

import warnings
warnings.filterwarnings("ignore")


class RagSystem:
    def __init__(self):
        load_dotenv()
        self.chat_model = ChatGoogleGenerativeAI(model=GEMINI_CHAT_MODEL, temperature=0.1)
        self.prompt_template = ChatPromptTemplate.from_messages(TEMPLATE)
        self.embeddings = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
        self.db = Chroma(persist_directory=CHROMA_DIR, embedding_function=self.embeddings, collection_name=COLLECTION_NAME)
        if self.db._collection.count() == 0:
            print("ChromaDB is empty. Starting ingestion...")
            ingest_system = RagSystemIngest()
            ingest_system.ingest()
            self.db = Chroma(
                persist_directory=CHROMA_DIR,
                embedding_function=self.embeddings,
                collection_name=COLLECTION_NAME
            )
            print(f"Documents ingested: {self.db._collection.count()}")

    def retrieve(self, query: str):
        retrieved_documents = self.db.similarity_search(
            query=query,
            k=5
        )

        formatted = []
        for doc in retrieved_documents:
            source = doc.metadata.get("source", "unknown_source")
            page = doc.metadata.get("page")

            formatted.append(
                {
                    "source": source,
                    "page": int(page)+1,
                    "content": doc.page_content
                }
            )

        return {
            "context": formatted,
            "question": query
        }

    def generate_answer(self, query: str):
        chain = RunnablePassthrough() | RunnableLambda(self.retrieve) | self.prompt_template | self.chat_model | StrOutputParser()
        result = chain.invoke(query)
        return result

    
    def answer_with_sources(self, query: str):
        retrieved = self.retrieve(query)

        chain = (
            self.prompt_template
            | self.chat_model
            | StrOutputParser()
        )

        answer = chain.invoke(retrieved)

        return {
            "answer": answer,
            "sources": retrieved["context"],
        }
