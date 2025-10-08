from fastapi import APIRouter, HTTPException
from transformers import pipeline
import requests
from PIL import Image
from io import BytesIO

router = APIRouter()

# Initialize the model as None. It will be loaded on the first request.
captioner_pipeline = None

@router.post("/infer")
def generate_caption(payload: dict):
    """
    Accepts a JSON payload with an "input" key containing a URL to an image.
    Returns a JSON object with an "output" key containing the generated caption.
    Loads the model on the first request (lazy loading).
    """
    global captioner_pipeline

    # Lazy loading: If the model is not loaded, load it.
    if captioner_pipeline is None:
        try:
            print("Loading image captioning model for the first time...")
            captioner_pipeline = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
            print("Image captioning model loaded successfully.")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Image captioning model could not be loaded: {e}")

    if "input" not in payload:
        raise HTTPException(status_code=400, detail="Payload must contain an 'input' field with an image URL.")

    image_url = payload["input"]

    try:
        # Fetch the image from the URL
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Open the image using Pillow
        image = Image.open(BytesIO(response.content))

        # Generate the caption
        caption_result = captioner_pipeline(image)

        # The output from this pipeline is a list of dictionaries
        return {"output": caption_result[0]["generated_text"]}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image from URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during image captioning: {e}")