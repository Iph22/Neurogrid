from fastapi import APIRouter, HTTPException
import pandas as pd
import re
import json
from typing import Any, Dict, List

router = APIRouter()

def clean_text(text: str) -> str:
    """Clean and normalize text data"""
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
    return text

def normalize_numbers(data: Any) -> Any:
    """Normalize numeric data"""
    if isinstance(data, (int, float)):
        return float(data)
    elif isinstance(data, str):
        try:
            return float(data)
        except ValueError:
            return data
    return data

def filter_data(data: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to data"""
    if not filters:
        return data
    
    filtered_data = []
    for item in data:
        include = True
        for key, condition in filters.items():
            if key not in item:
                continue
            
            if condition.get("min") is not None and item[key] < condition["min"]:
                include = False
                break
            if condition.get("max") is not None and item[key] > condition["max"]:
                include = False
                break
            if condition.get("equals") is not None and item[key] != condition["equals"]:
                include = False
                break
        
        if include:
            filtered_data.append(item)
    
    return filtered_data

@router.post("/infer")
def preprocess_data(payload: dict):
    """
    Preprocessing Node: Cleans, normalizes, and transforms data
    Accepts input data and preprocessing parameters.
    Returns processed data ready for AI model consumption.
    """
    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field.")
    
    input_data = payload["input"]
    
    # Extract preprocessing parameters
    operations = payload.get("operations", ["clean_text"])
    filters = payload.get("filters", {})
    
    try:
        # Handle different input types
        if isinstance(input_data, dict):
            if "data" in input_data:
                data = input_data["data"]
                data_type = input_data.get("type", "unknown")
            else:
                data = input_data
                data_type = "json"
        else:
            data = input_data
            data_type = "raw"
        
        processed_data = data
        
        # Apply preprocessing operations
        if "clean_text" in operations:
            if isinstance(processed_data, str):
                processed_data = clean_text(processed_data)
            elif isinstance(processed_data, list):
                processed_data = [
                    {**item, **{k: clean_text(v) if isinstance(v, str) else v 
                               for k, v in item.items()}} 
                    if isinstance(item, dict) else clean_text(str(item))
                    for item in processed_data
                ]
            elif isinstance(processed_data, dict):
                processed_data = {
                    k: clean_text(v) if isinstance(v, str) else v 
                    for k, v in processed_data.items()
                }
        
        if "normalize_numbers" in operations:
            if isinstance(processed_data, list):
                processed_data = [
                    {**item, **{k: normalize_numbers(v) for k, v in item.items()}} 
                    if isinstance(item, dict) else normalize_numbers(item)
                    for item in processed_data
                ]
            elif isinstance(processed_data, dict):
                processed_data = {
                    k: normalize_numbers(v) for k, v in processed_data.items()
                }
            else:
                processed_data = normalize_numbers(processed_data)
        
        # Apply filters if data is a list of dictionaries
        if "filter" in operations and isinstance(processed_data, list) and filters:
            processed_data = filter_data(processed_data, filters)
        
        # Remove empty or null values if specified
        if "remove_empty" in operations:
            if isinstance(processed_data, list):
                processed_data = [item for item in processed_data if item]
            elif isinstance(processed_data, dict):
                processed_data = {k: v for k, v in processed_data.items() if v is not None and v != ""}
        
        return {
            "output": {
                "data": processed_data,
                "type": data_type,
                "operations_applied": operations,
                "record_count": len(processed_data) if isinstance(processed_data, list) else 1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during preprocessing: {str(e)}")
