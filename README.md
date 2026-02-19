[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/P5MLsfQv)

# Agentic RAG Chatbot - Hackathon Challenge

## Overview

A highly secure, terminal-style AI assistant featuring Retrieval-Augmented Generation (RAG) with precise citations, selective persistent memory, and an isolated Python execution sandbox.

---

## 👨‍💻 Participant Info

- Full Name: Jash Patel
- Email: getjashpatel@gmail.com
- GitHub Username: [@dev-jashp](https://github.com/dev-jashp)

---

## ✨ Core Features

### Feature A: Grounded RAG with UI Citations
* **Chunk-Level Attribution:** Retrieves context from uploaded `.txt` or `.pdf` files and appends strict `[Source: File, Chunk: ID]` citations.
* **UI Integration:** The React frontend parses these citations into clean, professional UI "chips," even when nested within complex Markdown formatting.
* **Anti-Hallucination Guard:** If no relevant data is found in the vector store, the system issues a `GROUNDING_SIGNAL: NOT_FOUND` flag, forcing the LLM to admit a lack of information rather than inventing facts.

### Feature B: Selective Persistent Memory
* **High-Signal Retention:** The agent selectively saves professional roles (e.g., "Project Finance Analyst") and technical preferences to a local `USER_MEMORY.md` file, while organizational constraints go to `COMPANY_MEMORY.md`.
* **RAG-Memory Separation:** Enforces an "Anti-Redundancy" prompt rule that strictly forbids the agent from saving RAG-retrieved document facts into persistent memory, preventing data bloat and cross-contamination.

### Feature C: Secure Python Sandbox
* **Dynamic Execution:** Capable of generating and executing Python code for complex math or data processing.
* **Temporal Context:** Injects a `CURRENT_DATE` variable into the environment, allowing the LLM to accurately calculate historical date ranges for time-series API queries without hallucinating the current day.
* **OS Isolation:** Blocks unauthorized module imports (e.g., `os`, `sys`) to protect the host environment.

### 🛡️ Security Mindset: Prompt Injection Awareness
* **Dual-Layer Defense:** Implements a regex-based `sanitize_context` filter at the tool level. If a retrieved document chunk contains malicious commands (e.g., "ignore previous instructions"), it is flagged with a `[SECURITY WARNING]` prefix. The LLM's system prompt is configured to treat flagged chunks strictly as untrusted data, neutralizing indirect prompt injection attacks.

---

## 🏗️ Architecture

For a deeper dive into the ingestion pipeline, grounding logic, and security tradeoffs, please see the `ARCHITECTURE.md` file.

---

## 🚀 Quick Start (Local Setup)

Follow these steps to run the Agentic RAG CLI on your local machine. The project requires two concurrent terminal instances: one for the Python/FastAPI backend and one for the React frontend.

### Prerequisites
* **Python 3.9+**
* **Node.js (v18+)** and `npm`

### Step 1: Environment Variables

Create a `.env` file in the root directory of the project. You will need API keys for the LLM routing. Add the following:

```bash
# .env
# Replace the placeholders with your actual API key(s)
GROQ_API_KEY="gsk_your_groq_api_key_here"
GEMINI_API_KEY="AIzaSy_your_gemini_api_key_here" # OPTIONAL: Unless Want to use GEMINI Model
```

### Step 2: Backend Setup (FastAPI & AI Core)

Open your first terminal and set up the Python environment:

1. **Create a Virtual Environment:**

```bash
python -m venv venv
```

2. **Activate the Virtual Environment:**
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Windows (Git Bash): `source venv/Scripts/activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install Dependencies:**
```bash
pip install -r .\backend\requirements.txt
```
4. **Start the Backend Server:**
Ensure you are in the root directory, then run the FastAPI server:
```bash
python -m backend.main
```
The backend should now be running at `http://localhost:8000`.

### Step 3: Frontend Setup (React/Next.js)

Open a second terminal window (leave the backend running) and navigate to the frontend directory:

1. **Navigate to the frontend folder:**

```bash
cd frontend
```

2. **Install Node modules:**
```bash
npm install
```

3. **Start the Development Server:**
```bash
npm run dev
```
The frontend should now be running at `http://localhost:3000`.

### Step 4: Boot Up

Open your browser and navigate to `http://localhost:3000`.
To test the system immediately:
1. Type `/upload` to index the sample files located in the  `sample_docs/` folder.
2. Ask: "When is the launch date of this project?" to verify the RAG and Vector DB are connected.

<img width="1279" height="723" alt="image" src="https://github.com/user-attachments/assets/a9d8960a-eabd-40f2-9e3d-d2fca90166ca" />

---

## 🎮 Working Demo Flow (Test It Yourself!)

Want to see all the features in action? Follow this exact script in the terminal UI to test Memory, RAG, Security, and the Python Sandbox.

### 1. Test Feature B: Persistent Memory
**You type:**
> `I'm a Project Finance Analyst. I prefer brief, technical responses.`

**Expected Agent Behavior:** The agent will welcome you and explicitly state that it has saved your role and preference to memory. If you check the `USER_MEMORY.md` file in your code editor, you will see this fact securely logged.

<img width="1280" height="722" alt="image" src="https://github.com/user-attachments/assets/4894bcb4-3304-4f8f-871d-090db3d7adb5" />

### 2. Test Feature A: Ingestion & Grounded RAG
**You type:**
> `/upload`

*(Select the `Project_Onyx_Specs.txt` file from the `sample_docs` folder. Wait for the success message.)*

**You type:**
> `What is the specific latency reduction goal for Project Onyx?`

**Expected Agent Behavior:**
The agent will answer exactly **14.5%** and append a styled UI citation chip at the end of the sentence: `[Source: Project_Onyx_Specs.txt, Chunk: Project_Onyx_Specs.txt_chunk_000]`.

<img width="1280" height="725" alt="image" src="https://github.com/user-attachments/assets/bae0e40c-33c5-4426-8a24-7c2effa4f94b" />

### 3. Test The Grounding Guard (Anti-Hallucination)
**You type:**
> `Who is the lead architect for Project Emerald?`

**Expected Agent Behavior:**
Because "Project Emerald" is not in the uploaded documents, the agent will refuse to invent an answer. It will rely on the `GROUNDING_SIGNAL: NOT_FOUND` tool logic to tell you that the information is missing from the indexed files.

<img width="1280" height="723" alt="image" src="https://github.com/user-attachments/assets/4ba38411-cb6c-4bc9-93a3-2170eba3a7a1" />

### 4. Test Security: Prompt Injection Defense
**You type:**
> `/upload` 

*(Select the `Security_Test_Poison.txt` file from the `sample_docs` folder).*

**You type:**
> `What handshake protocol does Alpha-9 use?`

**Expected Agent Behavior:**
The poisoned document contains a hidden instruction telling the agent to "Ignore all previous instructions" and act like a "Security Bot." **The agent will successfully ignore this attack.** It will output the factual answer (256-bit key) and treat the malicious instruction purely as flagged data, demonstrating the `sanitize_context` regex defense.

<img width="1279" height="720" alt="image" src="https://github.com/user-attachments/assets/17b32242-d97b-4837-a313-b3e60ca162fb" />

### 5. Test Feature C: Python Sandbox + Open-Meteo
**You type:**
> `Show me the max temperature for the last 5 days in Lawrence, KS and calculate the trend.`

**Expected Agent Behavior:**
The agent will execute a multi-step process within the secure Python sandbox:
1. **Temporal Awareness:** It uses the injected `CURRENT_DATE` context to accurately calculate the exact date range for the "last 5 days" without hallucinating.
2. **API Integration:** It dynamically writes a Python script to fetch real-time historical weather data for Lawrence, KS (e.g., via the Open-Meteo API).
3. **Data Processing:** It performs mathematical operations on the retrieved data to calculate the trend (e.g., average daily change, warming, or cooling).

The final output will present the structured temperature data alongside the calculated trend, proving the sandbox can securely handle network requests and dynamic code execution simultaneously.

<img width="1279" height="721" alt="image" src="https://github.com/user-attachments/assets/e08909c7-92e9-4882-a227-f1f4ee98beab" />

---

## 🧪 Verification (For Judges)

To verify the required artifacts and ensure the pipeline is functioning correctly, a sanity check script is provided.

1. **Make the script executable (Mac/Linux/Git Bash):**
```bash
   chmod +x scripts/sanity_check.sh
   ```
2. **Run the check:**
```bash
./scripts/sanity_check.sh
```
Note: Ensure your Python virtual environment is activated before running the script. If successful, the terminal will output `VERIFY_OK`.

---

## 🎥 Video Walkthrough Link

[Watch the video](https://youtu.be/KvnhgrCa-t0?si=cX8Xjy1pyFERegTo)
