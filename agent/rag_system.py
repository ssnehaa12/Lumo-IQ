from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

class DocumentationRAG:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.bucket_name = os.getenv('GCS_DOCS_BUCKET')
        
        print("🔍 Initializing RAG System...")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None
        self._load_and_index_documents()
        print("✓ RAG System initialized\n")
    
    def _load_and_index_documents(self):
        print("📚 Loading documents from Cloud Storage...")
        storage_client = storage.Client(project=self.project_id)
        bucket = storage_client.bucket(self.bucket_name)
        
        documents = []
        blobs = bucket.list_blobs()
        for blob in blobs:
            if blob.name.endswith('.md'):
                print(f"   Loading: {blob.name}")
                content = blob.download_as_text()
                doc = Document(page_content=content, metadata={"source": blob.name, "bucket": self.bucket_name})
                documents.append(doc)
        
        print(f"✓ Loaded {len(documents)} documents")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        print(f"✓ Created {len(splits)} document chunks")
        
        self.vectorstore = Chroma.from_documents(documents=splits, embedding=self.embeddings, persist_directory="./chroma_db")
        print("✓ Vector store created")
    
    def search(self, query: str, k: int = 3) -> str:
        if not self.vectorstore:
            return "Documentation not available"
        docs = self.vectorstore.similarity_search(query, k=k)
        if not docs:
            return "No relevant documentation found"
        context_parts = [f"--- Document {i} (Source: {doc.metadata['source']}) ---\n{doc.page_content}\n" for i, doc in enumerate(docs, 1)]
        return "\n".join(context_parts)
