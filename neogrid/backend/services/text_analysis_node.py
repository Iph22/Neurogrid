from fastapi import APIRouter, HTTPException
from ..models.base_models import RequestEnvelope, ResponseEnvelope
import uuid

# Create a new router for this node
router = APIRouter()

# In-memory "model" for demonstration purposes.
# In a real-world scenario, you would load a proper model (e.g., from a file).
def analyze_sentiment(text: str) -> dict:
    """
    Dummy sentiment analysis function.
    Replace this with a real model inference call.
    """
    if "positive" in text.lower():
        return {"sentiment": "positive", "score": 0.9}
    elif "negative" in text.lower():
        return {"sentiment": "negative", "score": 0.8}
    else:
        return {"sentiment": "neutral", "score": 0.5}

@router.post("/infer", response_model=ResponseEnvelope)
async def infer(request: RequestEnvelope):
    """
    The main inference endpoint for this text analysis node.
    It expects a 'text' field in the request payload.
    """
    if "text" not in request.payload:
        raise HTTPException(status_code=400, detail="Payload must contain a 'text' field.")

    text_to_analyze = request.payload["text"]

    # Perform the analysis
    analysis_result = analyze_sentiment(text_to_analyze)

    # Wrap the result in the standard response envelope
    response = ResponseEnvelope(
        id=request.id,
        result=analysis_result,
        meta={"node_id": "text_analysis_node", "status": "success"}
    )
    return response