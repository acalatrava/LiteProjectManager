from peewee import *
from .base import BaseModel
from enum import Enum
import datetime
from app.schemas.users import UserInDB


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    id = CharField(primary_key=True)
    username = CharField(unique=True)
    password = CharField()
    salt = CharField()
    role = CharField(default=UserRole.USER.value)
    name = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)

    def is_admin(self):
        return self.role == UserRole.ADMIN.value

    def to_dict(self):
        user_schema = UserInDB(
            id=self.id,
            username=self.username,
            role=self.role,
            name=self.name,
            created_at=self.created_at,
            is_active=self.is_active
        )
        return user_schema.model_dump()
