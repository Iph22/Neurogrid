import pytest

VALID_CODE = """
import os

class MyClass:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}")

def my_function():
    return True
"""

INVALID_CODE = """
def my_function(
    return False
"""

def test_code_analyzer_valid_code(client):
    """
    Tests the code analyzer node with a valid Python code string.
    It expects a 'success' status and a summary of the code structure.
    """
    response = client.post("/nodes/code_analyzer/infer", json={"input": VALID_CODE})

    assert response.status_code == 200
    json_response = response.json()
    assert "output" in json_response
    output = json_response["output"]
    assert output["status"] == "success"
    assert "summary" in output
    summary = output["summary"]
    assert summary["function_count"] == 3  # __init__, greet, and my_function
    assert summary["class_count"] == 1
    assert summary["import_count"] == 1
    assert summary["total_lines"] > 5

def test_code_analyzer_invalid_code(client):
    """
    Tests the code analyzer node with a Python code string containing a syntax error.
    It expects an 'error' status and details about the syntax error.
    """
    response = client.post("/nodes/code_analyzer/infer", json={"input": INVALID_CODE})

    assert response.status_code == 200
    json_response = response.json()
    assert "output" in json_response
    output = json_response["output"]
    assert output["status"] == "error"
    assert output["error_type"] == "SyntaxError"
    assert "details" in output
    assert "line" in output["details"]
    assert "message" in output["details"]

def test_code_analyzer_no_input(client):
    """
    Tests the code analyzer node with a missing 'input' field.
    It expects a 400 Bad Request error.
    """
    response = client.post("/nodes/code_analyzer/infer", json={})
    assert response.status_code == 400
    assert "detail" in response.json()