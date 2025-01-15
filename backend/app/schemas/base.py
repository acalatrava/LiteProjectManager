from pydantic import BaseModel, ConfigDict
from typing import List, Optional


# Response Schema
class DefaultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: int
    error: str | None = None
    result: str | None = None
