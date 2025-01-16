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

# Email Configuration
SMTP_SERVER = config("SMTP_SERVER", default="")
SMTP_PORT = config("SMTP_PORT", cast=int, default=587)
SMTP_USER = config("SMTP_USER", default="")
SMTP_PASSWORD = config("SMTP_PASSWORD", cast=Secret, default="")
EMAIL_FROM = config("EMAIL_FROM", default="")
EMAIL_FROM_NAME = config("EMAIL_FROM_NAME", default=PROJECT_NAME)
EMAIL_ENABLED = config("EMAIL_ENABLED", cast=bool, default=False)
