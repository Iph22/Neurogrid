from fastapi import APIRouter, HTTPException
from transformers import pipeline

router = APIRouter()

# Initialize the model as None. It will be loaded on the first request.
sentiment_analyzer_pipeline = None

@router.post("/infer")
def analyze_sentiment_endpoint(payload: dict):
    """
    Accepts a JSON payload with an "input" key containing the text to be analyzed.
    Returns a JSON object with an "output" key containing the sentiment analysis result.
    Loads the model on the first request (lazy loading).
    """
    global sentiment_analyzer_pipeline

    # Lazy loading: If the model is not loaded, load it.
    if sentiment_analyzer_pipeline is None:
        try:
            print("Loading sentiment analysis model for the first time...")
            sentiment_analyzer_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            print("Sentiment analysis model loaded successfully.")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Sentiment analysis model could not be loaded: {e}")

    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field.")

    text = payload["input"]

    try:
        # Perform sentiment analysis
        result = sentiment_analyzer_pipeline(text)
        # The output from the pipeline is a list of dictionaries
        return {"output": result[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during sentiment analysis: {e}")