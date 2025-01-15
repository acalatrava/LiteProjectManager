from fastapi import APIRouter


class BaseEndpoint:
    def __init__(self):
        self.router = APIRouter()

    def add_api_route(self, *args, **kwargs):
        self.router.add_api_route(*args, **kwargs)

    def get_router(self):
        return self.router
