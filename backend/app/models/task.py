from peewee import *
from datetime import datetime
from .base import BaseModel
from .project import Project
from .user import User


class Task(BaseModel):
    id = CharField(primary_key=True)
    project = ForeignKeyField(Project, backref='tasks')
    name = CharField()
    description = TextField()
    assigned_to = ForeignKeyField(User, backref='assigned_tasks', null=True)
    created_by = ForeignKeyField(User, backref='created_tasks')
    status = CharField(default='pending')  # pending, in_progress, completed
    start_date = DateTimeField()
    deadline = DateTimeField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
