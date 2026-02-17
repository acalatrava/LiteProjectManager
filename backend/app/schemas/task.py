from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    name: constr(min_length=1, max_length=200)
    description: constr(max_length=5000)
    project_id: str
    start_date: datetime
    deadline: datetime


class TaskCreate(TaskBase):
    assigned_to_id: Optional[str] = None
    parent_task_id: Optional[str] = None


class TaskUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=200)] = None
    description: Optional[constr(max_length=5000)] = None
    project_id: Optional[str] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    assigned_to_id: Optional[str] = None
    parent_task_id: Optional[str] = None


class Task(TaskBase):
    id: str
    assigned_to_id: Optional[str]
    created_by_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    parent_task_id: Optional[str]
    subtasks: List['Task'] = []
