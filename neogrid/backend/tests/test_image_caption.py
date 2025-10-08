import pytest

# A reliable, publicly accessible image URL for testing.
# Using a static image from Wikipedia to minimize flakiness.
SAMPLE_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat_paw_close_up.jpg/800px-Cat_paw_close_up.jpg"
INVALID_IMAGE_URL = "http://this-is-not-a-real-url.com/image.jpg"

@pytest.mark.skip(reason="This test is slow and depends on an external URL.")
def test_image_caption_success(client):
    """
    Tests the image captioning node with a valid image URL.
    It expects a successful response and a non-empty caption string.
    This test is skipped by default because it's slow and requires internet access.
    """
    response = client.post("/nodes/image_caption/infer", json={"input": SAMPLE_IMAGE_URL})

    assert response.status_code == 200
    json_response = response.json()
    assert "output" in json_response
    assert isinstance(json_response["output"], str)
    assert len(json_response["output"]) > 0

def test_image_caption_no_input(client):
    """
    Tests the image captioning node with a missing 'input' field.
    It expects a 400 Bad Request error.
    """
    response = client.post("/nodes/image_caption/infer", json={})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_image_caption_invalid_url(client):
    """
    Tests the image captioning node with an invalid or unreachable URL.
    It expects a 400-level error, indicating the image could not be fetched.
    """
    response = client.post("/nodes/image_caption/infer", json={"input": INVALID_IMAGE_URL})
    # The service should return a client error (4xx) because the input URL is invalid.
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Failed to fetch image" in response.json()["detail"]