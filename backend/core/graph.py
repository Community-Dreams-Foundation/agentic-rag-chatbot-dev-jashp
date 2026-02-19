import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from backend.tools.rag_tool import retrieve_context
from backend.tools.memory_tool import save_memory, get_memory
from backend.tools.sandbox_tool import execute_python
from backend.core.prompts import SYSTEM_PROMPT

load_dotenv()

@tool
def search_documents(query: str) -> str:
    """
    Search the uploaded documents for context. 
    Returns the technical context or a 'NOT_FOUND' signal.
    """
    context = retrieve_context(query)
    # The Grounding Guard
    if not context or "No relevant information found" in context:
        return "GROUNDING_SIGNAL: NOT_FOUND. The requested information is missing from all uploaded documents."
    return context

# 2. Add save_memory to the agent's toolkit
tools = [search_documents, save_memory, get_memory, execute_python]


# ** If you want to use Gemini
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0) 
llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

agent_executor = create_agent(llm, tools=tools, system_prompt=SYSTEM_PROMPT)