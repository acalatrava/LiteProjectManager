import uuid
from fastapi import Depends, FastAPI, HTTPException, status, APIRouter, Form
from app.core import config
from app.api.v1.endpoints.userinfo import UserInfoEndpoint
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.db.relational import Users
from app.schemas.users import RegisterUserModel
from app.services.authentication import admin_user_check, user_check
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from app.db.database import get_db
from peewee import Database
from app.api.v1.endpoints.users import UsersEndpoint
from app.api.v1.endpoints.projects import ProjectsEndpoint
from app.api.v1.endpoints.tasks import TasksEndpoint
from app.api.v1.endpoints.gantt import GanttEndpoint
from app.api.v1.endpoints.comments import CommentsEndpoint


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


# Initialize FastAPI app
app = FastAPI(title=config.PROJECT_NAME, version=config.PROJECT_VERSION)

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add database dependency


async def get_db_session():
    with get_db() as session:
        yield session


# Create new user
@app.post("/signup",
          response_model=dict,
          tags=["authentication"],
          summary="Register a new user",
          description="Creates a new user account with the provided credentials"
          )
async def signup(
    form_data: RegisterUserModel,
    db: Database = Depends(get_db_session)
):
    """
    Register a new user with the following information:

    - **username**: Email address that will be used for login
    - **password**: Secret password for authentication
    - **name**: Optional full name of the user
    """
    user = Users.insert_new_user(username=form_data.username, password=form_data.password, name=form_data.name)

    # Create a login token
    if user:
        token = Users.create_auth_token(user.id)
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user"
        )


# Token authentication (login)
@app.post("/token",
          response_model=dict,
          tags=["authentication"],
          summary="Login to get access token",
          description="Authenticate user and return access token"
          )
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Login with username and password to get access token:

    - **username**: Email address used during registration
    - **password**: Account password
    """
    result = Users.get_user_by_username_and_password(
        username=form_data.username,
        password=form_data.password
    )

    if result:
        user, token = result
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Include endpoints
api_app = APIRouter(
    prefix="/api/v1",
    tags=["api"],
    responses={
        404: {"description": "Not found"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)

api_app.include_router(
    UserInfoEndpoint().get_router(),
    prefix="/userinfo",
    tags=["users"],
    dependencies=[Depends(user_check)],
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {"id": "123", "username": "user@example.com", "name": "John Doe"}
                }
            }
        }
    }
)

api_app.include_router(
    UsersEndpoint().get_router(),
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(user_check)],
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123",
                        "username": "user@example.com",
                        "name": "John Doe",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2024-03-20T10:00:00"
                    }
                }
            }
        }
    }
)

api_app.include_router(
    ProjectsEndpoint().get_router(),
    prefix="/projects",
    tags=["projects"]
)

api_app.include_router(
    TasksEndpoint().get_router(),
    prefix="/tasks",
    tags=["tasks"]
)

api_app.include_router(
    GanttEndpoint().get_router(),
    prefix="/gantt",
    tags=["gantt"]
)

api_app.include_router(
    CommentsEndpoint().get_router(),
    prefix="/comments",
    tags=["comments"],
    dependencies=[Depends(user_check)]
)

app.include_router(api_app)

# If ../build folder exists, serve it as static files
if os.path.exists("../build"):
    app.mount("/", SPAStaticFiles(directory="../build", html=True), name="spa-static-files")
else:
    @app.get("/",
             tags=["status"],
             summary="API Status",
             description="Check if the API is running"
             )
    async def root():
        """
        Returns a simple message indicating the API is running but the frontend build is not found
        """
        return {"message": "build folder not found!"}
