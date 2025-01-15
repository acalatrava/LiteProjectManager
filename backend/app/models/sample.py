from peewee import *
from datetime import datetime
from .base import BaseModel


class Sample(BaseModel):
    id = CharField(primary_key=True)
    date = DateTimeField()
    info = TextField()
