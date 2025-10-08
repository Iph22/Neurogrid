import pytest

def test_sentiment_positive(client):
    """
    Tests the sentiment analysis node with a positive text.
    It expects a 'POSITIVE' label in the output.
    """
    response = client.post("/nodes/sentiment/infer", json={"input": "NeuroGrid is an amazing and wonderful platform!"})

    assert response.status_code == 200
    json_response = response.json()
    assert "output" in json_response
    assert "label" in json_response["output"]
    assert "score" in json_response["output"]
    assert json_response["output"]["label"] == "POSITIVE"
    assert isinstance(json_response["output"]["score"], float)

def test_sentiment_negative(client):
    """
    Tests the sentiment analysis node with a negative text.
    It expects a 'NEGATIVE' label in the output.
    """
    response = client.post("/nodes/sentiment/infer", json={"input": "I am very disappointed with the results, this is terrible."})

    assert response.status_code == 200
    json_response = response.json()
    assert "output" in json_response
    assert "label" in json_response["output"]
    assert json_response["output"]["label"] == "NEGATIVE"

def test_sentiment_no_input(client):
    """
    Tests the sentiment node with a missing 'input' field.
    It expects a 400 Bad Request error.
    """
    response = client.post("/nodes/sentiment/infer", json={"text": "this is not the right key"})
    assert response.status_code == 400
    assert "detail" in response.json()