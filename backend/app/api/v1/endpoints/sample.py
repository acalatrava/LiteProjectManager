from fastapi import Path, Query, Body
from typing import List, Optional
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.base import DefaultResponse
from app.schemas.sample import SampleModel, SampleResponse, SampleInput
from app.db.relational import Samples
from app.services.authentication import user_check
from fastapi import Depends

import json


class SampleEndpoint(BaseEndpoint):

    def __init__(self):
        super().__init__()

        # Routes
        self.router.get("/", response_model=SampleResponse)(self.get)

        # Add data
        self.router.post("/", response_model=DefaultResponse)(self.add)

        # Clean database
        self.router.delete("/", response_model=DefaultResponse)(self.deleteAll)

        # Delete data
        self.router.delete("/{id}", response_model=DefaultResponse)(self.delete)

    async def get(self, userinfo=Depends(user_check)) -> SampleResponse:
        # Get the list of info
        results = Samples.get_all_data()
        if results:
            return SampleResponse(results=results, total_results=len(results), errors=[])
        else:
            return SampleResponse(results=[], total_results=0, errors=[])

    async def add(
        self,
        userinfo=Depends(user_check),
        sample: SampleInput = Body(..., description="Info to add")
    ) -> DefaultResponse:
        # Add new data
        try:
            Samples.insert_new_data(info=sample.info)
            return DefaultResponse(code=200, result="Data added successfully")
        except:
            return DefaultResponse(code=401, result="Error adding data")

    async def delete(self, id: str, userinfo=Depends(user_check)) -> DefaultResponse:
        # Delete data by id
        if Samples.delete_data_by_id(id=id):
            return DefaultResponse(code=200, result="Data deleted successfully")
        else:
            return DefaultResponse(code=401, result="Error deleting data")

    async def deleteAll(self, userinfo=Depends(user_check)) -> DefaultResponse:

        # Delete all data
        if Samples.delete_all_data():
            return DefaultResponse(code=200, result="Data deleted successfully")
        else:
            return DefaultResponse(code=401, result="Error deleting data")
