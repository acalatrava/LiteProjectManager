from peewee import *
from datetime import datetime
from .base import BaseModel
from .project import Project
from .user import User


class Task(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    description = TextField()
    project_id = CharField()
    start_date = DateTimeField()
    deadline = DateTimeField()
    assigned_to_id = CharField(null=True)  # Make sure this is nullable
    created_by_id = CharField()
    status = CharField(default='pending')  # pending, in_progress, completed
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
