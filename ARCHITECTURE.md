# Agentic RAG CLI - Architecture Overview

**Author:** Jash Patel
**GitHub:** `dev-jashp`

## Goal
Provide a brief, readable overview of how the Agentic RAG CLI works, detailing its ingestion pipeline, grounded retrieval system, selective memory logic, and secure sandbox execution. The system integrates a React-based terminal frontend with a Python (FastAPI) backend.


---

## High-Level Flow

### 1) Ingestion (Upload → Parse → Chunk)
- **Supported inputs:** Text documents (`.txt`, `.md`) and standard document formats (`.pdf`).
- **Parsing approach:** Text extraction and splitting into manageable contexts using standard text splitters.
- **Chunking strategy:** Documents are chunked and embedded using the `SentenceTransformer` (`all-MiniLM-L6-v2`) model to balance speed and semantic accuracy.
- **Metadata captured per chunk:**
  - `source`: filename (e.g. Project_Onyx_Specs.txt)
  - `chunk_id`: unique identifier for precise traceability (e.g. Project_Onyx_Specs.txt_chunk_000)

### 2) Indexing / Storage
- **Vector store choice:** Local ChromaDB instance for lightweight, embedded vector operations.
- **Persistence:** Stored locally in a `.chroma_data` directory to persist across application restarts.

### 3) Retrieval + Grounded Answering
- **Retrieval method:** Similarity search retrieving the top $k=4$ most relevant chunks.
- **Prompt Injection Awareness (Security):** Before retrieved chunks reach the LLM, a regex-based `sanitize_context` filter intercepts them. Malicious instructions (e.g., "ignore previous instructions") are wrapped in a `[SECURITY WARNING: POTENTIAL INJECTION DETECTED]` prefix. This forces the LLM to treat them as untrusted data rather than operational commands.
  
  
- **How citations are built:** A strict `[Source: <source>, Chunk: <chunk_id>]` citation string is appended to every chunk at the tool level. The frontend utilizes a custom AST (Abstract Syntax Tree) parser within `ReactMarkdown` to render these as clean, professional UI chips, ensuring they format correctly even when nested inside bolded text.
- **Failure behavior:** If the similarity search yields no relevant chunks, the retrieval tool returns a hardcoded `GROUNDING_SIGNAL: NOT_FOUND` string. The LLM's system prompt recognizes this signal and explicitly refuses to hallucinate an answer.

### 4) Memory System (Selective)
- **What counts as “high-signal” memory:** Professional roles (e.g., Software Engineer, Data Analyst, Project Finance Analyst) and explicit technical constraints or formatting preferences.
- **What you explicitly do NOT store:** RAG-retrieved document facts, temporary conversation states, personal daily habits, or sensitive PII.
- **How you decide when to write:** The LLM evaluates user input against strict prompt constraints. If a high-signal identity marker is detected, it triggers the `save_memory` tool and explicitly confirms the action to the user in the CLI.
- **Format written to:**
  - `USER_MEMORY.md` (Personal identities and user-specific technical preferences)
  - `COMPANY_MEMORY.md` (Organizational constraints and global standards)

### 5) Optional: Safe Tooling (Python Sandbox)
- **Tool interface shape:** A Python sandbox execution environment for dynamic mathematical calculations and API calls (e.g., Open-Meteo for weather data).
- **Safety boundaries:**
  - **Sandbox Isolation:** Unauthorized module imports (e.g., `os`, `sys`) are blocked via regex to prevent the LLM from accessing the host operating system.
  - **Temporal Context Injection:** A `CURRENT_DATE` variable is injected directly into the execution environment. This allows the LLM to calculate accurate historical date ranges for time-series API queries without guessing the current day.

---

## Tradeoffs & Next Steps
- **Tradeoffs:** A major architectural challenge was "Memory Over-fitting," where the LLM attempted to save RAG-retrieved document facts into persistent memory. This was resolved by implementing an "Anti-Redundancy" prompt rule, establishing a strict boundary between short-term document retrieval (Feature A) and long-term markdown memory (Feature B).
- **Next Steps:** With more time, the system would be expanded to include:
  - **File Management Tools:** Implementing CLI commands to dynamically re-index, delete, or inspect specific document chunks directly within the ChromaDB vector store.
  - **Simple Evaluation Harness:** Building an automated test suite with predefined questions and expected citations to ensure grounding accuracy and prevent regressions as the LLM model evolves.
  - **Streaming Responses:** Upgrading the FastAPI backend and React frontend to support real-time token streaming, providing a more fluid and responsive user experience during complex tool executions.
