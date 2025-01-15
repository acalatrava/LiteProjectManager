from peewee import Model
from app.db.database import DB


class BaseModel(Model):
    class Meta:
        database = DB
