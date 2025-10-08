from fastapi import APIRouter, HTTPException
import json
import pandas as pd
from io import StringIO
from typing import Any, Dict, List

router = APIRouter()

def format_as_text(data: Any) -> str:
    """Format data as readable text"""
    if isinstance(data, str):
        return data
    elif isinstance(data, dict):
        return json.dumps(data, indent=2)
    elif isinstance(data, list):
        if all(isinstance(item, dict) for item in data):
            # Format as table-like structure
            result = []
            for i, item in enumerate(data):
                result.append(f"Record {i+1}:")
                for key, value in item.items():
                    result.append(f"  {key}: {value}")
                result.append("")
            return "\n".join(result)
        else:
            return "\n".join(str(item) for item in data)
    else:
        return str(data)

def format_as_json(data: Any) -> Dict:
    """Format data as JSON structure"""
    if isinstance(data, dict):
        return data
    elif isinstance(data, list):
        return {"items": data, "count": len(data)}
    else:
        return {"value": data, "type": type(data).__name__}

def format_as_csv(data: Any) -> str:
    """Format data as CSV string"""
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    elif isinstance(data, dict):
        df = pd.DataFrame([data])
        return df.to_csv(index=False)
    else:
        # Single value CSV
        return f"value\n{data}"

def format_as_summary(data: Any) -> Dict:
    """Create a summary of the data"""
    summary = {
        "type": type(data).__name__,
        "preview": None,
        "statistics": {}
    }
    
    if isinstance(data, str):
        summary["preview"] = data[:200] + "..." if len(data) > 200 else data
        summary["statistics"] = {
            "length": len(data),
            "word_count": len(data.split()) if data else 0
        }
    elif isinstance(data, list):
        summary["preview"] = data[:3] if len(data) <= 3 else data[:3] + ["..."]
        summary["statistics"] = {
            "count": len(data),
            "item_types": list(set(type(item).__name__ for item in data))
        }
    elif isinstance(data, dict):
        summary["preview"] = {k: v for i, (k, v) in enumerate(data.items()) if i < 5}
        summary["statistics"] = {
            "keys": len(data.keys()),
            "key_names": list(data.keys())[:10]
        }
    else:
        summary["preview"] = str(data)
        summary["statistics"] = {"value": data}
    
    return summary

@router.post("/infer")
def format_output(payload: dict):
    """
    Output Node: Formats and presents final workflow results
    Accepts processed data and formatting parameters.
    Returns formatted output in the specified format.
    """
    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field.")
    
    input_data = payload["input"]
    output_format = payload.get("output_format", "json")
    include_summary = payload.get("include_summary", True)
    
    try:
        # Extract data from input
        if isinstance(input_data, dict) and "data" in input_data:
            data = input_data["data"]
            metadata = {k: v for k, v in input_data.items() if k != "data"}
        else:
            data = input_data
            metadata = {}
        
        # Format output based on requested format
        formatted_output = None
        
        if output_format == "text":
            formatted_output = format_as_text(data)
        elif output_format == "json":
            formatted_output = format_as_json(data)
        elif output_format == "csv":
            formatted_output = format_as_csv(data)
        elif output_format == "summary":
            formatted_output = format_as_summary(data)
        else:
            # Default to JSON
            formatted_output = format_as_json(data)
        
        result = {
            "output": formatted_output,
            "format": output_format,
            "metadata": metadata
        }
        
        # Add summary if requested
        if include_summary and output_format != "summary":
            result["summary"] = format_as_summary(data)
        
        return {"output": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting output: {str(e)}")
