# backend/tools/sandbox_tool.py
import sys
import pandas as pd
import requests    
import re
from io import StringIO
from langchain_core.tools import tool
from datetime import datetime

# SECURITY GUARD: Patterns that could be used for sandbox escapes or file system access
FORBIDDEN_PATTERNS = [
    r"import\s+os", r"import\s+subprocess", r"import\s+sys", r"import\s+shutil",
    r"from\s+os", r"from\s+subprocess", r"os\.", r"sys\.", r"open\(", 
    r"eval\(", r"exec\(", r"__builtin__", r"getattr", r"socket"
]

@tool
def execute_python(code: str) -> str:
    """Executes Python code in a secured environment with pd, requests, math, and datetime pre-loaded."""
    code = code.strip().replace("```python", "").replace("```", "").strip()

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return f"SECURITY_ERROR: The command matching '{pattern}' is restricted."

    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    
    try:
        # Pre-loading the modules into the environment so the agent doesn't have to import them
        exec_globals = {
            "pd": pd,
            "requests": requests,
            "print": print,
            "math": __import__('math'),
            "datetime": __import__('datetime'),
            # EXPLICIT DATE INJECTION
            "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d"),
            "__builtins__": __builtins__
        }
        
        exec(code, exec_globals)
        
        output = redirected_output.getvalue()
        return f"REAL_EXECUTION_RESULT:\n{output}" if output else "No output printed."
    except Exception as e:
        return f"EXECUTION_ERROR: {str(e)}"
    finally:
        sys.stdout = old_stdout