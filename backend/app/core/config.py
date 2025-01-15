from starlette.config import Config
from starlette.datastructures import Secret
import os

# Try to load .env file, but don't fail if it doesn't exist
config = Config(".env") if os.path.exists(".env") else Config(environ=os.environ)

PROJECT_NAME = config("PROJECT_NAME", default="TestApp")
PROJECT_VERSION = config("PROJECT_VERSION", default="0.1")
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="test_secret_key_123")
SQLITE_PATH = config("SQLITE_PATH", default=":memory:")
AUTH_TOKEN_LIFETIME = config("AUTH_TOKEN_LIFETIME", cast=int, default=86400)
WHITELIST_DOMAIN = config("WHITELIST_DOMAIN", default="")
