# FastAPI application and endpoints

import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import our working intelligence layer!
from backend.ingest.document_parser import ingest_document
from backend.core.graph import agent_executor
import traceback

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
async def ingest_files(files: List[UploadFile] = File(...)):
    """Receives multiple files, processes them, and indexes them."""
    try:
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        
        total_chunks = 0
        processed_files = []

        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Pass to our upgraded document parser
            result = ingest_document(file_path, file.filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
            if result.get("status") == "success":
                total_chunks += result.get("chunks_indexed", 0)
                processed_files.append(file.filename)
            
        return {"status": "success", "processed_files": processed_files, "total_chunks": total_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        inputs = {"messages": [("user", request.message)]}
        response = agent_executor.invoke(inputs)
        
        final_message = response["messages"][-1].content
        
        if isinstance(final_message, list):
            final_message = "".join(
                block["text"] for block in final_message if isinstance(block, dict) and "text" in block
            )
        
        return {"reply": final_message}
    except Exception as e:
        # FIX: Print the exact error to the terminal so we can debug it
        print("\n=== FASTAPI CRASH LOG ===")
        print(traceback.format_exc())
        print("=========================\n")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)