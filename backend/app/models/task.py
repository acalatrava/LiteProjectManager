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
    # Reference to parent task if this is a subtask
    parent_task_id = ForeignKeyField('self', null=True, backref='subtasks')

    def get_subtasks(self):
        return self.subtasks  # Use the backref created by ForeignKeyField

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "start_date": self.start_date,
            "deadline": self.deadline,
            "assigned_to_id": self.assigned_to_id,
            "created_by_id": self.created_by_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "parent_task_id": self.parent_task_id.id if self.parent_task_id else None
        }
