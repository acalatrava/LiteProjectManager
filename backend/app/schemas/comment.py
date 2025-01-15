from pydantic import BaseModel
from datetime import datetime


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    task_id: str


class Comment(CommentBase):
    id: str
    task_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
