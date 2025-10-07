# NeuroGrid - A Modular AI Workflow Platform

NeuroGrid is a starter repository for building a modular, service-oriented AI workflow platform. It provides a complete, runnable foundation with a FastAPI backend and a React/Next.js frontend, designed for creating, visualizing, and executing sequences of AI tasks.

## Core Concepts

- **Modular Nodes**: Each AI function (e.g., text analysis, image recognition) is a self-contained service with a standard API. This makes it easy to add new capabilities without altering the core system.
- **Workflow Orchestration**: The backend includes a simple orchestrator that executes a series of nodes based on a user-defined workflow.
- **Visual Editor**: The frontend features a drag-and-drop interface using React Flow, allowing users to build and visualize workflows by connecting nodes.
- **Standardized Communication**: All API communication uses a consistent JSON envelope, ensuring predictability and ease of debugging.

## Project Structure

```
neogrid/
├── backend/
│   ├── main.py           # FastAPI entrypoint, workflow orchestrator
│   ├── models/           # Pydantic models for API requests/responses
│   └── services/         # Self-contained AI nodes (e.g., text_analysis_node.py)
├── frontend/
│   ├── pages/            # Next.js pages (e.g., the main workflow editor page)
│   ├── components/       # Reusable React components (NodeCard, WorkflowEditor)
│   └── utils/            # Utility functions (API calls, data formatting)
├── data/
│   ├── demo_data.csv     # Sample data for testing nodes
│   └── preprocess.py     # Script for data loading and cleaning
├── README.md             # This file
└── requirements.txt      # Python dependencies for the backend
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js and npm (or yarn)
- An environment to run Python (e.g., `venv`)

### 1. Backend Setup

First, set up and run the FastAPI backend.

```bash
# Navigate to the project root
cd neogrid

# Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install Python dependencies
pip install -r requirements.txt

# Run the backend server
cd backend
uvicorn main:app --reload
```

The backend server will start on `http://127.0.0.1:8000`. You can access the auto-generated API documentation at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

In a separate terminal, set up and run the Next.js frontend.

```bash
# Navigate to the frontend directory
cd neogrid/frontend

# Install Node.js dependencies
npm install

# Run the frontend development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## How to Use

1.  **Open the Frontend**: Navigate to `http://localhost:3000` in your browser.
2.  **Add Nodes**: Click the "Add Text Analysis Node" button to add a new processing node to the canvas.
3.  **Execute Workflow**: Click the "Execute Workflow" button. This sends the current workflow configuration (all the "Text Analysis" nodes on the canvas) to the backend.
4.  **View Results**: An alert will pop up with the JSON response from the backend, showing the results from each node in the workflow.

## Extending NeuroGrid

### Adding a New AI Node

To add a new AI capability (e.g., an image resizing node):

1.  **Create the Service**:
    -   Add a new file in `neogrid/backend/services/`, for example, `image_resize_node.py`.
    -   Inside this file, create a new FastAPI `APIRouter`.
    -   Define the core logic for your node and expose it via an `/infer` endpoint, following the pattern in `text_analysis_node.py`.
2.  **Register the Node**:
    -   In `neogrid/backend/main.py`, import your new router.
    -   Include the router in the main FastAPI app: `app.include_router(image_resize_node.router, prefix="/nodes/image_resize", tags=["AI Nodes"])`.
3.  **Update the Frontend**:
    -   In `neogrid/frontend/components/WorkflowEditor.js`, add a new button to create your image resize node.
    -   When adding the node, make sure to set the `node.data.nodeType` to `image_resize` (matching the prefix in `main.py`) and provide the correct `params` structure.

This modular approach ensures that the core orchestration logic remains unchanged, making the platform highly extensible.