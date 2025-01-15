from peewee import *
from datetime import datetime
from .base import BaseModel
from .user import User


class AuthToken(BaseModel):
    id = CharField(primary_key=True)  # UUID
    user = ForeignKeyField(User, backref='tokens')
    token = CharField(unique=True)
    created_at = DateTimeField(default=datetime.now)
    expires_at = DateTimeField()
    is_active = BooleanField(default=True)

    def is_valid(self) -> bool:
        return self.is_active and self.expires_at > datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'is_active': self.is_active
        }
