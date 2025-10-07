from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models.base_models import WorkflowExecutionRequest, ResponseEnvelope
from .services import text_analysis_node
import httpx
import uuid

app = FastAPI(
    title="NeuroGrid Backend",
    description="A modular AI workflow platform.",
    version="0.1.0",
)

# --- Middleware ---
# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
# Include the routers from different service nodes
# Each node is a self-contained module with its own endpoints
app.include_router(text_analysis_node.router, prefix="/nodes/text_analysis", tags=["AI Nodes"])


# --- Workflow Orchestration ---
# A simple orchestrator that calls nodes sequentially.
# In a real system, this would be replaced by a more robust solution like Celery, Airflow, or a custom scheduler.
@app.post("/workflow/execute", response_model=ResponseEnvelope)
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Executes a workflow defined by a sequence of nodes.

    This endpoint simulates a workflow by making HTTP requests to the individual
    AI node services. This microservices-style architecture allows for scalability
    and modularity.
    """
    current_request_id = str(uuid.uuid4())
    results = []

    # In this simple orchestrator, we assume a base URL for the services.
    # In a containerized environment, this would be the service discovery address.
    base_url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient() as client:
        for node in request.nodes:
            node_id = node.get("node_id")
            params = node.get("params", {})

            # Construct the URL for the node's inference endpoint
            node_url = f"{base_url}/nodes/{node_id}/infer"

            # Create the request envelope for the node
            node_request_payload = {
                "id": str(uuid.uuid4()),
                "payload": params,
                "meta": {"source": "workflow_orchestrator"}
            }

            try:
                # Call the node's /infer endpoint
                response = await client.post(node_url, json=node_request_payload, timeout=10.0)
                response.raise_for_status()  # Raise an exception for bad status codes

                node_result = response.json()
                results.append(node_result)

            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Error calling node '{node_id}': {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An unexpected error occurred in node '{node_id}': {e}")

    # Wrap the final results in a response envelope
    final_response = ResponseEnvelope(
        id=current_request_id,
        result={"workflow_outputs": results},
        meta={"status": "workflow_completed"}
    )

    return final_response

@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to NeuroGrid!"}