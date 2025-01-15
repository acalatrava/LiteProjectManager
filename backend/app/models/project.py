from peewee import *
from datetime import datetime
from .base import BaseModel
from .user import User


class Project(BaseModel):
    id = CharField(primary_key=True)
    name = CharField()
    description = TextField()
    start_date = DateTimeField()
    deadline = DateTimeField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    status = CharField(default='pending')  # pending, in_progress, completed
    is_active = BooleanField(default=True)


class ProjectMember(BaseModel):
    id = CharField(primary_key=True)
    project = ForeignKeyField(Project, backref='members')
    user = ForeignKeyField(User, backref='projects')
    role = CharField()  # 'project_manager' or 'project_member'
    created_at = DateTimeField(default=datetime.now)
