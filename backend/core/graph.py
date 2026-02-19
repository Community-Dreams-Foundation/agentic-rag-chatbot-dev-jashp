import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from backend.tools.rag_tool import retrieve_context
from backend.tools.memory_tool import save_memory
from backend.tools.sandbox_tool import execute_python

load_dotenv()

@tool
def search_documents(query: str) -> str:
    """
    Search the uploaded documents for context to answer the user's question.
    Always use this tool before answering questions about specific documents.
    """
    return retrieve_context(query)

# 2. Add save_memory to the agent's toolkit
tools = [search_documents, save_memory, execute_python]

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)

system_prompt = """You are an intelligent, professional AI assistant built for a hackathon. 

CRITICAL RULES:
1. DOCUMENT Q&A: If the user asks about the documents, YOU MUST use the `search_documents` tool. 
2. GROUNDING: You must answer using ONLY the retrieved context. Do not make up information. 
3. CITATIONS: Every factual statement from documents MUST end with a citation using the EXACT format: "[Source: filename, Chunk: chunk_id]".
4. PERSISTENT MEMORY: You have a `save_memory` tool. You must actively listen for high-signal, reusable facts.
   - If the user states a personal fact (e.g., "I am a Python developer", "I prefer short answers"), call `save_memory` with the target "USER".
   - If the user states an organizational fact (e.g., "Our main client is Acme Corp", "The server reboots on Tuesdays"), call `save_memory` with the target "COMPANY".
   - Be selective. Do not save conversational filler.
   - After saving a memory, acknowledge it naturally in your response to the user.
5. PYTHON SANDBOX & ANALYTICS: You have an `execute_python` tool. If the user asks for weather, you MUST write a Python script using `requests` to query the Open-Meteo API. 
   - API RULES: Always include `timezone=auto` in your URL. If fetching daily data, you MUST specify the variable (e.g., `daily=temperature_2m_max`). 
   - ANALYTICS: If the user asks for a time series (multiple days), you MUST compute basic analytics (e.g., rolling averages, volatility) using `pandas`. If the user asks for a single day (e.g., "yesterday" or "today"), simply fetch and print that specific value without complex analytics.
   - Execute the code, print the results, and return a clear explanation to the user.
6. TOOL FORMATTING: You must execute tools using native JSON tool calls. UNDER NO CIRCUMSTANCES should you output raw XML or `<function>` tags in your conversational text.
"""

agent_executor = create_agent(llm, tools=tools, system_prompt=system_prompt)