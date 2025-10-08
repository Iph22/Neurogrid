from fastapi import APIRouter, HTTPException
import json
import pandas as pd
from io import StringIO

router = APIRouter()

@router.post("/infer")
def process_input(payload: dict):
    """
    Input Node: Handles various input types (text, JSON, CSV data)
    Accepts a JSON payload with an "input" key and optional "input_type" parameter.
    Returns processed data in a standardized format.
    """
    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field.")
    
    input_data = payload["input"]
    input_type = payload.get("input_type", "text")
    
    try:
        if input_type == "text":
            # Simple text input
            return {"output": {"data": input_data, "type": "text"}}
        
        elif input_type == "json":
            # JSON input - parse and validate
            if isinstance(input_data, str):
                parsed_data = json.loads(input_data)
            else:
                parsed_data = input_data
            return {"output": {"data": parsed_data, "type": "json"}}
        
        elif input_type == "csv":
            # CSV input - convert to structured data
            if isinstance(input_data, str):
                df = pd.read_csv(StringIO(input_data))
                data = df.to_dict('records')
            else:
                data = input_data
            return {"output": {"data": data, "type": "csv"}}
        
        elif input_type == "number":
            # Numeric input
            try:
                num_data = float(input_data)
                return {"output": {"data": num_data, "type": "number"}}
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid number format")
        
        else:
            # Default: treat as raw data
            return {"output": {"data": input_data, "type": "raw"}}
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing input: {str(e)}")
