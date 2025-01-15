from fastapi import Query, Depends
from typing import Optional
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.search import SearchResponse, SearchResultItem
from app.services.authentication import user_check
from app.db.relational import Samples


class SearchEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()
        self.router.get("/", response_model=SearchResponse)(self.search)

    async def search(
        self,
        q: str = Query(..., description="Search term"),
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        userinfo=Depends(user_check)
    ) -> SearchResponse:
        # Search samples using the query
        results = Samples.search_samples(query=q, skip=skip, limit=limit)

        # Convert samples to search results
        search_results = [
            SearchResultItem(
                id=sample.id,
                content=sample.info
            )
            for sample in results
        ]

        return SearchResponse(
            results=search_results,
            total_results=len(search_results)
        )
