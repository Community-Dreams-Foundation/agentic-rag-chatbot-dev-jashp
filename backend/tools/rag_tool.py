import os
from langchain_community.vectorstores import Chroma

# UPDATE: We use a different, more stable embeddings wrapper
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

# Pointing to the exact same local database directory
CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".chroma_data")

def get_embedding_model():
    # This wrapper avoids the 'is_offline_mode' bug we saw earlier
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def retrieve_context(query: str, k: int = 3) -> str:
    """
    Retrieves relevant document chunks from ChromaDB and formats them with strict citations.
    This will be registered as a tool for our LangGraph agent.
    """
    if not os.path.exists(CHROMA_DB_DIR):
        return "System Warning: No documents have been indexed yet. Please ask the user to upload a document first."

    # Connect to the existing local Chroma database
    embedding_function = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=embedding_function
    )

    # Search for the most relevant chunks
    results = vectorstore.similarity_search(query, k=k)

    if not results:
        return "No relevant information found in the uploaded documents."

    # Format the output to explicitly pair the content with its required citation
    formatted_context = []
    for doc in results:
        source = doc.metadata.get("source", "Unknown_File")
        chunk_id = doc.metadata.get("chunk_id", "Unknown_Chunk")
        
        # This exact string format is what we will instruct the LLM to append to its answers
        citation = f"[Source: {source}, Chunk: {chunk_id}]"
        
        chunk_text = (
            f"--- START CHUNK ---\n"
            f"Content: {doc.page_content}\n"
            f"Required Citation: {citation}\n"
            f"--- END CHUNK ---"
        )
        formatted_context.append(chunk_text)

    return "\n\n".join(formatted_context)

# Quick local test block
if __name__ == "__main__":
    test_query = "What is the role described in the document?"
    print(f"Searching for: '{test_query}'\n")
    print(retrieve_context(test_query))