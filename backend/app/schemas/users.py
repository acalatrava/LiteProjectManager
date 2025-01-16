from pydantic import BaseModel, ConfigDict, constr, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = None
    password: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: str
    created_at: datetime

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


class UserResponse(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# This is the Pydantic model for the user registration form
class RegisterUserModel(UserBase):
    password: constr(min_length=8)
