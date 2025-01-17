from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from .task import Task  # Import Task schema


class ProjectBase(BaseModel):
    name: str
    description: str
    start_date: datetime
    deadline: datetime


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    status: Optional[str] = None


class ProjectMemberBase(BaseModel):
    user_id: str
    role: str = 'project_member'


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
