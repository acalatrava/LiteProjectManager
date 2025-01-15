from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    name: str
    description: str
    project_id: str
    start_date: datetime
    deadline: datetime


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    status: Optional[str] = None
    assigned_to_id: Optional[str] = None


class Task(TaskBase):
    id: str
    assigned_to_id: Optional[str]
    created_by_id: str
    status: str
    created_at: datetime
    updated_at: datetime
