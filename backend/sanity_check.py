# Sanity Check Script for Agentic RAG Chatbot Development

import os
import json
import traceback
from backend.tools.rag_tool import retrieve_context
from backend.tools.memory_tool import save_memory

def run_sanity_check():
    print("Initiating Hackathon Sanity Checks...")
    
    results = {
        "feature_a_rag": "failed",
        "feature_b_memory": "failed",
        "errors": []
    }

    # ---------------------------------------------------------
    # TEST 1: Feature A (RAG Retrieval)
    # ---------------------------------------------------------
    try:
        print("Testing Feature A (RAG Retrieval)...")
        # We query the ChromaDB directly bypassing the LLM to ensure the DB works
        context = retrieve_context("What are the requirements for a tutor?", k=1)
        
        if "System Warning" not in context and "No relevant information" not in context:
            results["feature_a_rag"] = "passed"
            print("✅ Feature A Passed")
        else:
            results["errors"].append("RAG retrieval returned no context. Ensure a document is indexed.")
            print("❌ Feature A Failed: No context returned.")
    except Exception as e:
        results["errors"].append(f"RAG Error: {str(e)}")
        print(f"❌ Feature A Error: {str(e)}")

    # ---------------------------------------------------------
    # TEST 2: Feature B (Persistent Memory)
    # ---------------------------------------------------------
    try:
        print("Testing Feature B (Persistent Memory)...")
        # We invoke the LangChain tool directly with the strict Pydantic schema
        mem_result = save_memory.invoke({
            "should_write": True,
            "target": "COMPANY",
            "summary": "Sanity check automated test memory.",
            "confidence": 0.99
        })
        
        if "Successfully saved" in mem_result:
            results["feature_b_memory"] = "passed"
            print("✅ Feature B Passed")
        else:
            results["errors"].append(f"Memory tool bypassed or failed: {mem_result}")
            print("❌ Feature B Failed")
    except Exception as e:
        results["errors"].append(f"Memory Error: {str(e)}")
        print(f"❌ Feature B Error: {str(e)}")

    # ---------------------------------------------------------
    # GENERATE ARTIFACTS
    # ---------------------------------------------------------
    # The judges explicitly require the output to be in an 'artifacts' folder
    root_dir = os.path.dirname(os.path.dirname(__file__))
    artifacts_dir = os.path.join(root_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    output_path = os.path.join(artifacts_dir, "sanity_output.json")
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\nSanity check complete. Results written to: {output_path}")

if __name__ == "__main__":
    run_sanity_check()