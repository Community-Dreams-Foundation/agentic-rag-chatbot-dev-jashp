import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".chroma_data")

def get_embedding_model():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def retrieve_context(query: str, k: int = 4) -> str:
    """Retrieves relevant document chunks from ChromaDB and formats them with strict citations."""
    if not os.path.exists(CHROMA_DB_DIR):
        return "System Warning: No documents have been indexed yet."

    embedding_function = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=embedding_function
    )

    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return "No relevant information found in the uploaded documents."

    formatted_context = []
    for doc in results:
        source = doc.metadata.get("source", "Unknown_File")
        chunk_id = doc.metadata.get("chunk_id", "Unknown_Chunk")
        
        citation = f"[Source: {source}, Chunk: {chunk_id}]"
        chunk_text = f"Content: {doc.page_content}\nRequired Citation: {citation}\n"
        formatted_context.append(chunk_text)

    return "\n\n".join(formatted_context)