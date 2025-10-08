from fastapi import APIRouter, HTTPException
import ast

router = APIRouter()

def analyze_python_code(code: str) -> dict:
    """
    Analyzes a string of Python code using the `ast` module.
    It checks for syntax errors and provides a basic summary of the code structure.
    """
    try:
        # Attempt to parse the code into an Abstract Syntax Tree
        tree = ast.parse(code)

        # If parsing is successful, extract some basic information
        analysis = {
            "status": "success",
            "summary": {
                "function_count": len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                "class_count": len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                "import_count": len([node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]),
                "total_lines": len(code.splitlines())
            }
        }
        return analysis

    except SyntaxError as e:
        # If parsing fails, report the syntax error
        return {
            "status": "error",
            "error_type": "SyntaxError",
            "details": {
                "line": e.lineno,
                "offset": e.offset,
                "message": e.msg
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "UnexpectedError",
            "message": str(e)
        }


@router.post("/infer")
def analyze_code(payload: dict):
    """
    Accepts a JSON payload with an "input" key containing Python code as a string.
    Returns a JSON object with an "output" key containing the analysis.
    """
    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field with code to analyze.")

    code_to_analyze = payload["input"]

    analysis_result = analyze_python_code(code_to_analyze)

    return {"output": analysis_result}