import os
from langchain_community.document_loaders import PyMuPDFLoader, BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".chroma_data")

def get_embedding_model():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def ingest_document(file_path: str, filename: str) -> dict:
    try:
        # Support both HTML and PDF
        if filename.lower().endswith('.html'):
            loader = BSHTMLLoader(file_path)
        else:
            loader = PyMuPDFLoader(file_path)
        documents = loader.load()
    except Exception as e:
        return {"status": "error", "message": f"Failed to parse document: {str(e)}"}

    # Smart chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = filename
        chunk.metadata["chunk_id"] = f"{filename}_chunk_{i:03d}"

    try:
        embedding_function = get_embedding_model()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory=CHROMA_DB_DIR
        )
    except Exception as e:
        return {"status": "error", "message": f"Failed to index: {str(e)}"}

    return {"status": "success", "chunks_indexed": len(chunks), "filename": filename}