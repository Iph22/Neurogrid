from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import httpx
import json

from .nodes import summarizer, image_caption, code_analyzer, sentiment, input_node, preprocessing_node, postprocessing_node, output_node
from .database import database, models, schemas
from .routers import auth
from .workflow_engine import workflow_engine

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
app.include_router(summarizer.router,
                   prefix="/nodes/summarizer", tags=["AI Nodes"])
app.include_router(image_caption.router,
                   prefix="/nodes/image_caption", tags=["AI Nodes"])
app.include_router(code_analyzer.router,
                   prefix="/nodes/code_analyzer", tags=["AI Nodes"])
app.include_router(
    sentiment.router, prefix="/nodes/sentiment", tags=["AI Nodes"])
app.include_router(input_node.router,
                   prefix="/nodes/input_node", tags=["Workflow Nodes"])
app.include_router(preprocessing_node.router,
                   prefix="/nodes/preprocessing_node", tags=["Workflow Nodes"])
app.include_router(postprocessing_node.router,
                   prefix="/nodes/postprocessing_node", tags=["Workflow Nodes"])
app.include_router(output_node.router,
                   prefix="/nodes/output_node", tags=["Workflow Nodes"])


# --- Node Registry ---
@app.get("/nodes/registry")
def get_node_registry():
    """Returns the list of available nodes from a JSON file."""
    import os
    from pathlib import Path
    
    # Get the directory where this main.py file is located
    current_dir = Path(__file__).parent
    registry_path = current_dir / "nodes" / "node_registry.json"
    
    try:
        with open(registry_path) as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail=f"Node registry not found at {registry_path}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Error reading node registry.")

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
    Executes a workflow with enhanced sequential processing and data passing.
    """
    db_workflow = db.query(models.Workflow).filter(
        models.Workflow.id == workflow_id,
        models.Workflow.user_id == current_user.id
    ).first()

    if not db_workflow:
        raise HTTPException(
            status_code=404, detail="Workflow not found or access denied.")

    workflow_config = db_workflow.config_json
    nodes = workflow_config.get("nodes", [])
    edges = workflow_config.get("edges", [])
    input_data = request_body.get("inputs", {})

    # Create workflow run record
    db_run = models.WorkflowRun(
        workflow_id=workflow_id,
        input_json=input_data,
        output_json={}
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    try:
        # Use enhanced workflow engine for execution
        results = await workflow_engine.execute_workflow(nodes, edges, input_data)
        
        # Update run record with results
        db_run.output_json = results
        db.commit()
        db.refresh(db_run)

        return db_run
        
    except Exception as e:
        # Update run record with error
        error_results = {"execution_error": str(e)}
        db_run.output_json = error_results
        db.commit()
        db.refresh(db_run)
        
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}
