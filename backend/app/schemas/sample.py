from typing import List
from pydantic import BaseModel
from datetime import datetime


class SampleModel(BaseModel):
    id: str
    date: datetime
    info: str


class SampleInput(BaseModel):
    info: str


class SampleResponse(BaseModel):
    results: List[SampleModel]
    total_results: int
    errors: List[str]
