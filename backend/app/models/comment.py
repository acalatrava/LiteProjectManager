from peewee import *
from datetime import datetime
from .base import BaseModel
from .user import User
from .task import Task


class Comment(BaseModel):
    id = CharField(primary_key=True)
    task_id = CharField()
    user_id = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
