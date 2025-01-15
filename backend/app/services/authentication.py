

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.db.relational import Users

# Initialize OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def admin_user_check(token: Annotated[str, Depends(oauth2_scheme)]):
    # This will check if the token is an admin
    if not Users.is_admin(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin permissions required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If the user is an admin, return the user object
    return Users.get_user_by_token(token)


async def user_check(token: Annotated[str, Depends(oauth2_scheme)]):
    # This will check if the token corresponds to a user
    user = Users.get_user_by_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return the user object
    return user
