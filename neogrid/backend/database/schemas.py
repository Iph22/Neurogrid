from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Workflow Schemas ---
class WorkflowBase(BaseModel):
    name: str
    config_json: Dict[str, Any]

class WorkflowCreate(WorkflowBase):
    pass

class Workflow(WorkflowBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# --- WorkflowRun Schemas ---
class WorkflowRunBase(BaseModel):
    input_json: Optional[Dict[str, Any]] = None
    output_json: Optional[Dict[str, Any]] = None

class WorkflowRunCreate(WorkflowRunBase):
    pass

class WorkflowRun(WorkflowRunBase):
    id: int
    workflow_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True