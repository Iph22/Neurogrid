import pytest

# A long article for testing summarization
SAMPLE_ARTICLE = """
Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and other animals.
Leading AI textbooks define the field as the study of "intelligent agents": any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.
Colloquially, the term "artificial intelligence" is often used to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".
As machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect.
For instance, optical character recognition is frequently excluded from things considered to be AI, having become a routine technology.
Modern machine capabilities generally classified as AI include successfully understanding human speech, competing at the highest level in strategic game systems (such as chess and Go), autonomously operating cars, and intelligent routing in content delivery networks and military simulations.
"""

def test_summarizer_success(client):
    """
    Tests the summarizer node with a valid input.
    It expects a successful response and a non-empty summary.
    """
    response = client.post("/nodes/summarizer/infer", json={"input": SAMPLE_ARTICLE})

    assert response.status_code == 200
    json_response = response.json()
    assert "output" in json_response
    assert isinstance(json_response["output"], str)
    assert len(json_response["output"]) > 0
    # The summary should be shorter than the original article
    assert len(json_response["output"]) < len(SAMPLE_ARTICLE)

def test_summarizer_no_input(client):
    """
    Tests the summarizer node with a missing 'input' field.
    It expects a 400 Bad Request error.
    """
    response = client.post("/nodes/summarizer/infer", json={"data": "this is not the right key"})
    assert response.status_code == 400
    assert "detail" in response.json()

@pytest.mark.skip(reason="This test can be slow as it might download the model.")
def test_summarizer_integration(client):
    """
    A more comprehensive integration test that checks the content of the summary.
    This is skipped by default to keep tests fast.
    """
    response = client.post("/nodes/summarizer/infer", json={"input": "AI is a field of study in computer science."})
    assert response.status_code == 200
    assert "output" in response.json()
    # A simple check to see if the summary contains a keyword.
    assert "AI" in response.json()["output"]