# PDF parsing, semantic chunking, and Chroma indexing
import os
import uuid
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

# Use a local directory for Chroma so `make sanity` works instantly without Docker/Cloud DBs
CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".chroma_data")

def get_embedding_model():
    # Using a fast, open-source embedding model that runs locally
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def ingest_document(file_path: str, filename: str) -> dict:
    """
    Parses a PDF, chunks it smartly, adds citation metadata, and indexes it into ChromaDB.
    """
    print(f"Starting ingestion for {filename}...")

    # 1. Parse the PDF
    try:
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
    except Exception as e:
        return {"status": "error", "message": f"Failed to parse document: {str(e)}"}

    # 2. Smart Chunking
    # Keeps paragraphs together, providing better semantic context for the LLM
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Inject Citation Metadata
    # This is critical for the hackathon requirement to provide citations
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = filename
        chunk.metadata["chunk_id"] = f"chunk_{i:03d}"
        chunk.metadata["page"] = chunk.metadata.get("page", 0) + 1 # 1-indexed pages

    # 4. Index into Local Vector Store
    try:
        embedding_function = get_embedding_model()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory=CHROMA_DB_DIR
        )
        vectorstore.persist()
    except Exception as e:
        return {"status": "error", "message": f"Failed to index into ChromaDB: {str(e)}"}

    print(f"Successfully indexed {len(chunks)} chunks from {filename}.")
    
    return {
        "status": "success", 
        "chunks_indexed": len(chunks),
        "filename": filename
    }

# Quick local test block
# How to Test in Local Environment:
# 1. Place a sample PDF (e.g., "sample.pdf", "sample.pdf") in the root directory of the project.
# 2. Run this script directly (e.g., `python document_parser.py`).
if __name__ == "__main__":
    # You can test this by dropping a sample PDF in the root and running this script
    ingest_document("VT_Role.pdf", "VT_Role.pdf")
    pass