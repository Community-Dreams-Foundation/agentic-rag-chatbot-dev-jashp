import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent

# NEW: Import the Gemini integration
from langchain_google_genai import ChatGoogleGenerativeAI

# Import the retrieval tool we just built
from backend.tools.rag_tool import retrieve_context

# Load environment variables (API Key)
load_dotenv()

# 1. Wrap our python function into a LangChain Tool
@tool
def search_documents(query: str) -> str:
    """
    Search the uploaded documents for context to answer the user's question.
    Always use this tool before answering questions about specific documents, architecture, or domain knowledge.
    """
    return retrieve_context(query)

tools = [search_documents]

# 2. Initialize the Gemini LLM
# We use gemini-2.5-flash as it is extremely fast and great at tool execution
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 3. The System Prompt (Enforcing Hackathon Rules)
system_prompt = """You are an intelligent, professional AI assistant built for a hackathon. 
Your primary job is to answer the user's questions based on uploaded documents.

CRITICAL RULES:
1. If the user asks a question about the documents, YOU MUST use the `search_documents` tool to retrieve context.
2. GROUNDING: You must answer using ONLY the retrieved context. Do not make up information.
3. CITATIONS (MANDATORY): Every single factual statement you make MUST end with a citation using the EXACT format provided in the retrieved context. 
   - Correct Example: "The architecture uses LangGraph [Source: ARCHITECTURE.md, Chunk: chunk_004]."
   - Incorrect Example: "The architecture uses LangGraph (Source 1)."
4. If the retrieved context does not contain the answer, politely state that you cannot find the information in the uploaded files.
"""

# 4. Compile the Agent Graph
agent_executor = create_agent(llm, tools=tools, system_prompt=system_prompt)

# --- Quick Local Test Block ---
if __name__ == "__main__":
    print("Testing Agentic Loop with Gemini...\n")
    
    # We simulate the user's message
    test_input = {"messages": [("user", "What are the requirements for a tutor according to the document?")]}
    
    # Run the graph
    for step in agent_executor.stream(test_input, stream_mode="values"):
        last_message = step["messages"][-1]
        last_message.pretty_print()