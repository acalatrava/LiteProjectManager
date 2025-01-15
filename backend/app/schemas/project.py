from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ProjectBase(BaseModel):
    name: str
    description: str
    start_date: datetime
    deadline: datetime


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    status: Optional[str] = None


class Project(ProjectBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    is_active: bool


class ProjectMemberBase(BaseModel):
    project_id: str
    user_id: str
    role: str  # 'project_manager' or 'project_member'


class ProjectMember(ProjectMemberBase):
    id: str
    created_at: datetime
