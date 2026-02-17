from pydantic import BaseModel, constr
from datetime import datetime


class CommentBase(BaseModel):
    content: constr(min_length=1, max_length=5000)


class CommentCreate(CommentBase):
    task_id: str


class Comment(CommentBase):
    id: str
    task_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
