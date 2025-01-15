from pydantic import BaseModel, Field
from typing import List


# Request Schema
class SearchRequest(BaseModel):
    query: str


# Response Schema
class SearchResultItem(BaseModel):
    id: str = Field(..., description="The unique identifier of the sample")
    content: str = Field(..., description="The sample information that matched the search")


class SearchResponse(BaseModel):
    results: List[SearchResultItem] = Field(..., description="List of matching samples")
    total_results: int = Field(..., description="Total number of results found")
