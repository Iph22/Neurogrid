from fastapi import APIRouter, HTTPException
from transformers import pipeline

router = APIRouter()

# Initialize the model as None. It will be loaded on the first request.
summarizer_pipeline = None

@router.post("/infer")
def summarize(payload: dict):
    """
    Accepts a JSON payload with an "input" key containing the text to be summarized.
    Returns a JSON object with an "output" key containing the summary.
    Loads the model on the first request (lazy loading).
    """
    global summarizer_pipeline

    # Lazy loading: If the model is not loaded, load it.
    if summarizer_pipeline is None:
        try:
            print("Loading summarizer model for the first time...")
            summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
            print("Summarizer model loaded successfully.")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Summarizer model could not be loaded: {e}")

    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field.")

    text = payload["input"]

    try:
        # Perform summarization
        summary = summarizer_pipeline(text, max_length=130, min_length=30, do_sample=False)
        return {"output": summary[0]["summary_text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during summarization: {e}")