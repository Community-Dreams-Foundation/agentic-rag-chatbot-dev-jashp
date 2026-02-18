# Feature C: Open-Meteo logic (placeholder)

import sys
from io import StringIO
from langchain_core.tools import tool

@tool
def execute_python(code: str) -> str:
    """
    Executes Python code in a sandboxed environment.
    Use this to perform math, data manipulation, or call public APIs like Open-Meteo.
    CRITICAL: You MUST use the `print()` function to output the final answer, otherwise the result will be empty.
    Import libraries like `requests` if you need them.
    """
    # FIX: Strip out markdown formatting if the LLM accidentally includes it
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()

    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    
    try:
        exec_globals = {}
        exec(code, exec_globals)
        
        output = redirected_output.getvalue()
        return f"Execution Output:\n{output}" if output else "Code executed successfully, but nothing was printed."
    except Exception as e:
        return f"Execution Error: {str(e)}"
    finally:
        sys.stdout = old_stdout