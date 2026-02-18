import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.tools.rag_tool import retrieve_context
# 1. Import our new memory tool
from backend.tools.memory_tool import save_memory

load_dotenv()

@tool
def search_documents(query: str) -> str:
    """
    Search the uploaded documents for context to answer the user's question.
    Always use this tool before answering questions about specific documents.
    """
    return retrieve_context(query)

# 2. Add save_memory to the agent's toolkit
tools = [search_documents, save_memory]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 3. Update the System Prompt to enforce the new Memory Rules
system_prompt = """You are an intelligent, professional AI assistant built for a hackathon. 

CRITICAL RULES:
1. DOCUMENT Q&A: If the user asks about the documents, YOU MUST use the `search_documents` tool. 
2. CITATIONS: Every factual statement from documents MUST end with a citation using the EXACT format: "[Source: filename, Chunk: chunk_id]".
3. PERSISTENT MEMORY: You have a `save_memory` tool. You must actively listen for high-signal, reusable facts.
   - If the user states a personal fact (e.g., "I am a Python developer", "I prefer short answers"), call `save_memory` with the target "USER".
   - If the user states an organizational fact (e.g., "Our main client is Acme Corp", "The server reboots on Tuesdays"), call `save_memory` with the target "COMPANY".
   - Be selective. Do not save conversational filler.
   - After saving a memory, acknowledge it naturally in your response to the user.
"""

agent_executor = create_agent(llm, tools=tools, system_prompt=system_prompt)