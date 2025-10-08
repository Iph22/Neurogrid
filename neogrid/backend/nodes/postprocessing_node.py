from fastapi import APIRouter, HTTPException
import json
import re
from typing import Any, Dict, List, Union

router = APIRouter()

def aggregate_results(data: List[Dict], aggregation_type: str = "concat") -> Any:
    """Aggregate multiple AI model results"""
    if not data:
        return None
    
    if aggregation_type == "concat":
        # Concatenate text results
        texts = []
        for item in data:
            if isinstance(item, dict) and "output" in item:
                texts.append(str(item["output"]))
            else:
                texts.append(str(item))
        return " ".join(texts)
    
    elif aggregation_type == "average":
        # Average numeric results
        numbers = []
        for item in data:
            if isinstance(item, (int, float)):
                numbers.append(item)
            elif isinstance(item, dict) and "score" in item:
                numbers.append(float(item["score"]))
        return sum(numbers) / len(numbers) if numbers else 0
    
    elif aggregation_type == "max_confidence":
        # Return result with highest confidence
        max_item = None
        max_confidence = -1
        for item in data:
            confidence = 0
            if isinstance(item, dict):
                confidence = item.get("confidence", item.get("score", 0))
            if confidence > max_confidence:
                max_confidence = confidence
                max_item = item
        return max_item
    
    elif aggregation_type == "merge":
        # Merge dictionary results
        merged = {}
        for item in data:
            if isinstance(item, dict):
                merged.update(item)
        return merged
    
    else:
        return data

def apply_confidence_threshold(data: Any, threshold: float = 0.5) -> Any:
    """Filter results based on confidence threshold"""
    if isinstance(data, dict) and "confidence" in data:
        if data["confidence"] >= threshold:
            return data
        else:
            return {"filtered": True, "reason": f"Confidence {data['confidence']} below threshold {threshold}"}
    
    elif isinstance(data, list):
        filtered_results = []
        for item in data:
            if isinstance(item, dict) and "confidence" in item:
                if item["confidence"] >= threshold:
                    filtered_results.append(item)
            else:
                filtered_results.append(item)
        return filtered_results
    
    return data

def format_ai_results(data: Any, format_type: str = "standard") -> Dict:
    """Format AI model results into standardized structure"""
    if format_type == "standard":
        return {
            "result": data,
            "confidence": data.get("confidence", 1.0) if isinstance(data, dict) else 1.0,
            "model_output": data
        }
    
    elif format_type == "classification":
        if isinstance(data, dict):
            return {
                "predicted_class": data.get("label", data.get("class", "unknown")),
                "confidence": data.get("score", data.get("confidence", 1.0)),
                "all_predictions": data
            }
        else:
            return {
                "predicted_class": str(data),
                "confidence": 1.0,
                "all_predictions": data
            }
    
    elif format_type == "text_generation":
        if isinstance(data, dict):
            return {
                "generated_text": data.get("generated_text", data.get("output", str(data))),
                "metadata": {k: v for k, v in data.items() if k != "generated_text"}
            }
        else:
            return {
                "generated_text": str(data),
                "metadata": {}
            }
    
    return {"formatted_result": data}

@router.post("/infer")
def postprocess_results(payload: dict):
    """
    Postprocessing Node: Processes and refines AI model outputs
    Accepts AI model results and postprocessing parameters.
    Returns refined, aggregated, and formatted results.
    """
    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field.")
    
    input_data = payload["input"]
    
    # Extract postprocessing parameters
    operations = payload.get("operations", ["format"])
    aggregation_type = payload.get("aggregation_type", "concat")
    confidence_threshold = payload.get("confidence_threshold", 0.0)
    format_type = payload.get("format_type", "standard")
    
    try:
        # Extract data from input
        if isinstance(input_data, dict) and "data" in input_data:
            data = input_data["data"]
        else:
            data = input_data
        
        processed_data = data
        
        # Apply postprocessing operations
        if "aggregate" in operations and isinstance(processed_data, list):
            processed_data = aggregate_results(processed_data, aggregation_type)
        
        if "confidence_filter" in operations:
            processed_data = apply_confidence_threshold(processed_data, confidence_threshold)
        
        if "format" in operations:
            processed_data = format_ai_results(processed_data, format_type)
        
        # Clean up text results
        if "clean_text" in operations and isinstance(processed_data, (str, dict)):
            if isinstance(processed_data, str):
                # Remove extra whitespace and normalize
                processed_data = re.sub(r'\s+', ' ', processed_data).strip()
            elif isinstance(processed_data, dict) and "generated_text" in processed_data:
                processed_data["generated_text"] = re.sub(r'\s+', ' ', processed_data["generated_text"]).strip()
        
        # Add processing metadata
        result = {
            "data": processed_data,
            "postprocessing": {
                "operations_applied": operations,
                "aggregation_type": aggregation_type if "aggregate" in operations else None,
                "confidence_threshold": confidence_threshold if "confidence_filter" in operations else None,
                "format_type": format_type if "format" in operations else None
            }
        }
        
        return {"output": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during postprocessing: {str(e)}")
