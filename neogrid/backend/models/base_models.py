from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class RequestEnvelope(BaseModel):
    """
    Standard request envelope for all API calls.
    """
    id: str = Field(..., description="Unique identifier for the request.")
    payload: Dict[str, Any] = Field(..., description="The actual data payload for the operation.")
    meta: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the request.")

class ResponseEnvelope(BaseModel):
    """
    Standard response envelope for all API calls.
    """
    id: str = Field(..., description="Corresponds to the request ID.")
    result: Dict[str, Any] = Field(..., description="The result of the operation.")
    meta: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the response.")

class WorkflowExecutionRequest(BaseModel):
    """
    Defines the structure for a workflow execution request.
    A workflow is a list of nodes to be executed in sequence.
    """
    nodes: list[Dict[str, Any]] # e.g., [{"node_id": "text_analyzer", "params": {"text": "some input"}}]