from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

PROJECT_NAME = config("PROJECT_NAME")
PROJECT_VERSION = config("PROJECT_VERSION")
SECRET_KEY = config("SECRET_KEY", cast=Secret)
SQLITE_PATH = config("SQLITE_PATH")
AUTH_TOKEN_LIFETIME = config("AUTH_TOKEN_LIFETIME", cast=int, default=86400)
