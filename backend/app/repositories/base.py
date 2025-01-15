from typing import Generic, TypeVar, Type
from peewee import Model

ModelType = TypeVar("ModelType", bound=Model)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, id: any) -> ModelType:
        return self.model.get_by_id(id)

    def get_all(self):
        return self.model.select()
