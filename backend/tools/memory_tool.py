# Feature B: Markdown memory writers (placeholder)

import os
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Define absolute paths to the root directory where the judges expect the markdown files
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
USER_MEMORY_PATH = os.path.join(ROOT_DIR, "USER_MEMORY.md")
COMPANY_MEMORY_PATH = os.path.join(ROOT_DIR, "COMPANY_MEMORY.md")

# We use Pydantic to force the LLM to output the exact decision structure requested by the judges
class MemoryInput(BaseModel):
    should_write: bool = Field(description="True ONLY if this is a high-signal, reusable fact worth remembering.")
    target: str = Field(description="Must be exactly 'USER' for personal facts or 'COMPANY' for org-wide learnings.")
    summary: str = Field(description="A concise, readable summary of the fact to remember.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0. Only write if >= 0.8.")

@tool("save_memory", args_schema=MemoryInput)
def save_memory(should_write: bool, target: str, summary: str, confidence: float) -> str:
    """
    Evaluates and saves selective, high-signal knowledge to persistent markdown memory.
    Use this immediately when the user states a preference, role, or an organizational fact.
    Do NOT store secrets or sensitive information.
    """
    if not should_write:
        return "Memory bypassed: Not a high-signal fact."
        
    if confidence < 0.8:
        return f"Memory bypassed: Confidence ({confidence}) is too low."

    if target.upper() not in ["USER", "COMPANY"]:
        return "Memory bypassed: Invalid target. Must be USER or COMPANY."

    # Determine which file to write to
    file_path = USER_MEMORY_PATH if target.upper() == "USER" else COMPANY_MEMORY_PATH
    
    # Ensure the files exist
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(f"# {target.upper()} MEMORY\n\n")

# Append the memory
    try:
        with open(file_path, "a") as f:
            # Added a leading newline to ensure it breaks away from any existing comments
            f.write(f"\n- {summary}\n")
        return f"Successfully saved memory to {target}_MEMORY.md: '{summary}'"
    except Exception as e:
        return f"System Error: Failed to save memory: {str(e)}"
    
@tool("get_memory")
def get_memory() -> str:
    """
    Retrieves all stored high-signal knowledge from both USER and COMPANY memory files.
    Always call this at the start of a session or when needing context on user preferences.
    """
    memories = []
    
    for path, label in [(USER_MEMORY_PATH, "USER"), (COMPANY_MEMORY_PATH, "COMPANY")]:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    content = f.read().strip()
                    if content:
                        memories.append(f"--- {label} MEMORY ---\n{content}")
            except Exception as e:
                memories.append(f"Error reading {label} memory: {str(e)}")
        else:
            memories.append(f"--- {label} MEMORY ---\n(Empty: No facts stored yet)")

    return "\n\n".join(memories)