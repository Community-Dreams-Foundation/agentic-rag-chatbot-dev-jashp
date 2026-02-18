# FastAPI application and endpoints

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our working intelligence layer!
from backend.ingest.document_parser import ingest_document
from backend.core.graph import agent_executor

app = FastAPI(title="Agentic RAG API")

# CRITICAL: Configure CORS so your NextJS frontend (port 3000) can talk to this backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected JSON payload for chat
class ChatRequest(BaseModel):
    message: str

@app.post("/api/ingest")
async def ingest_file(file: UploadFile = File(...)):
    """Receives a file from the UI, saves it temporarily, and indexes it into ChromaDB."""
    try:
        # 1. Create a safe temporary directory for uploads
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        # 2. Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. Pass it to our document parser
        result = ingest_document(file_path, file.filename)
        
        # 4. Clean up the temp file so we don't leak memory
        if os.path.exists(file_path):
            os.remove(file_path)
            
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Passes the user's message to the LangGraph agent and returns the response."""
    try:
        # Format the input exactly how our LangGraph expects it
        inputs = {"messages": [("user", request.message)]}
        
        # Invoke the agent synchronously for now to ensure stability
        response = agent_executor.invoke(inputs)
        
        # Extract the raw content from the AI's last message
        final_message = response["messages"][-1].content
        
        # FIX: Gemini often returns a list of dictionaries for its content. 
        # We must flatten it into a plain string so ReactMarkdown doesn't crash.
        if isinstance(final_message, list):
            final_message = "".join(
                block["text"] for block in final_message if isinstance(block, dict) and "text" in block
            )
        
        return {"reply": final_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)