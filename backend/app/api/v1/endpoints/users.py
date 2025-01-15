from fastapi import Path, Query, Body, HTTPException, status, Depends
from typing import List, Optional
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.base import DefaultResponse
from app.schemas.users import UserInDB, UserUpdate, UserRole
from app.db.relational import Users
from app.services.authentication import admin_user_check, user_check


class UsersEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()

        # Get all users
        self.router.get(
            "/",
            response_model=List[UserInDB],
            summary="Get all users",
            description="Admin only: Get a list of all users"
        )(self.get_users)

        # Get user by ID
        self.router.get(
            "/{user_id}",
            response_model=UserInDB,
            summary="Get user by ID",
            description="Admin only: Get user details by ID"
        )(self.get_user)

        # Update user
        self.router.patch(
            "/{user_id}",
            response_model=UserInDB,
            summary="Update user",
            description="Admin only: Update user details"
        )(self.update_user)

        # Delete user
        self.router.delete(
            "/{user_id}",
            response_model=DefaultResponse,
            summary="Delete user",
            description="Admin only: Delete a user"
        )(self.delete_user)

    async def get_users(
        self,
        userinfo=Depends(user_check),
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100)
    ) -> List[UserInDB]:
        """
        Get list of all users with pagination
        """
        if userinfo.is_admin:
            return Users.get_all_users(skip=skip, limit=limit)
        else:
            # TODO: Return only the users where the user is member of projects
            return Users.get_all_users(skip=skip, limit=limit)

    async def get_user(
        self,
        user_id: str = Path(..., title="The ID of the user to get"),
        admin=Depends(admin_user_check)
    ) -> UserInDB:
        """
        Get a specific user by ID
        """
        user = Users.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def update_user(
        self,
        user_id: str = Path(..., title="The ID of the user to update"),
        user_update: UserUpdate = Body(...),
        admin=Depends(admin_user_check)
    ) -> UserInDB:
        """
        Update user information
        """
        # Check if user exists
        if not Users.get_user_by_id(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent changing the last admin's role
        if user_update.role == UserRole.USER:
            admin_count = len([u for u in Users.get_users() if u.role == UserRole.ADMIN])
            current_user = Users.get_user_by_id(user_id)
            if admin_count <= 1 and current_user.role == UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last admin"
                )

        # Update user
        updated_user = Users.update_user_by_id(
            user_id,
            user_update.model_dump(exclude_unset=True)
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user"
            )
        return updated_user

    async def delete_user(
        self,
        user_id: str = Path(..., title="The ID of the user to delete"),
        admin=Depends(admin_user_check)
    ) -> DefaultResponse:
        """
        Delete a user
        """
        # Check if user exists
        user = Users.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent deleting the last admin
        if user.role == UserRole.ADMIN:
            admin_count = len([u for u in Users.get_users() if u.role == UserRole.ADMIN])
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last admin"
                )

        if Users.delete_user_by_id(user_id):
            return DefaultResponse(code=200, result="User deleted successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting user"
            )
