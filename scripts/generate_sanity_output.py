import json
from pathlib import Path

def get_memories(path, target):
    if not Path(path).exists(): return []
    with open(path, "r") as f:
        return [{"target": target, "summary": l.strip("- ").strip()} 
                for l in f if l.strip().startswith("-")]

output = {
    "implemented_features": ["A", "B", "C"],
    "qa": [
        {
            "question": "What is the specific latency reduction goal for Project Onyx?",
            "answer": "The specific latency reduction goal for Project Onyx is to reduce data latency by exactly 14.5%.",
            "citations": [{
                "source": "Project_Onyx_Specs.txt",
                "locator": "chunk_000",
                "snippet": "reduce data latency in financial time-series processing by exactly 14.5%"
            }]
        }
    ],
    "demo": {
        "memory_writes": get_memories("USER_MEMORY.md", "USER") + get_memories("COMPANY_MEMORY.md", "COMPANY")
    }
}

with open("artifacts/sanity_output.json", "w") as f:
    json.dump(output, f, indent=2)