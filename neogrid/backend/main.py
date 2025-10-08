from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx
import json

from .nodes import summarizer, image_caption, code_analyzer, sentiment
from .database import database, models, schemas, auth

# Create all database tables on startup
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="NeuroGrid Backend",
    description="A modular AI workflow platform.",
    version="0.3.0",
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(summarizer.router, prefix="/nodes/summarizer", tags=["AI Nodes"])
app.include_router(image_caption.router, prefix="/nodes/image_caption", tags=["AI Nodes"])
app.include_router(code_analyzer.router, prefix="/nodes/code_analyzer", tags=["AI Nodes"])
app.include_router(sentiment.router, prefix="/nodes/sentiment", tags=["AI Nodes"])


# --- Node Registry ---
@app.get("/nodes/registry")
def get_node_registry():
    """Returns the list of available nodes from a JSON file."""
    try:
        with open("neogrid/backend/nodes/node_registry.json") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Node registry not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading node registry.")

# --- Workflow CRUD Endpoints ---

@app.post("/workflows/", response_model=schemas.Workflow)
def create_workflow(
    workflow: schemas.WorkflowCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Create a new workflow for the current user."""
    db_workflow = models.Workflow(**workflow.dict(), user_id=current_user.id)
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@app.get("/workflows/", response_model=list[schemas.Workflow])
def get_user_workflows(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """List all workflows for the current user."""
    return db.query(models.Workflow).filter(models.Workflow.user_id == current_user.id).all()


# --- Workflow Orchestration ---
@app.post("/workflow/{workflow_id}/execute", response_model=schemas.WorkflowRun)
async def execute_workflow(
    workflow_id: int,
    request_body: dict = Body(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Executes a workflow, logs the run, and stores the results.
    """
    db_workflow = db.query(models.Workflow).filter(
        models.Workflow.id == workflow_id,
        models.Workflow.user_id == current_user.id
    ).first()

    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found or access denied.")

    workflow_config = db_workflow.config_json
    nodes = workflow_config.get("nodes", [])
    input_data = request_body.get("inputs", {})

    db_run = models.WorkflowRun(
        workflow_id=workflow_id,
        input_json=input_data,
        output_json={}
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    results = {}
    base_url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient() as client:
        for node in nodes:
            node_id = node.get("id")
            node_type = node.get("type")
            node_input = input_data.get(node_id, node.get("data", {}).get("input"))

            if node_input is None:
                results[node_id] = {"error": "No input provided for node."}
                continue

            node_url = f"{base_url}/nodes/{node_type}/infer"
            payload = {"input": node_input}

            try:
                response = await client.post(node_url, json=payload, timeout=30.0)
                response.raise_for_status()
                node_result = response.json()
                results[node_id] = node_result
            except Exception as e:
                error_detail = f"Error executing node '{node_type}' ({node_id}): {e}"
                results[node_id] = {"error": error_detail}

    db_run.output_json = results
    db.commit()
    db.refresh(db_run)

    return db_run


@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}