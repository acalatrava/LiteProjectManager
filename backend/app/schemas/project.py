from typing import List, Optional, Literal
from pydantic import BaseModel, constr
from datetime import datetime
from .task import Task  # Import Task schema


class ProjectBase(BaseModel):
    name: constr(min_length=1, max_length=200)
    description: constr(max_length=5000)
    start_date: datetime
    deadline: datetime


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    status: Optional[str] = None
    name: Optional[constr(min_length=1, max_length=200)] = None
    description: Optional[constr(max_length=5000)] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None


class ProjectMemberBase(BaseModel):
    user_id: str
    role: Literal['project_member', 'project_manager'] = 'project_member'


class ProjectMember(ProjectMemberBase):
    id: str
    project_id: str
    created_at: datetime


class Project(ProjectBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    tasks: List[Task] = []  # Add tasks field with default empty list
    members: List[ProjectMember] = []  # Add members field with default empty list

    class Config:
        from_attributes = True
