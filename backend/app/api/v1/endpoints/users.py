from fastapi import Path, Query, Body, HTTPException, status, Depends
from typing import List, Optional
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.base import DefaultResponse
from app.schemas.users import UserInDB, UserUpdate, UserRole, UserCreate
from app.db.relational import Users, Projects
from app.services.authentication import admin_user_check, user_check
import secrets
import string
from app.services.email_service import EmailService


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

        # Create new user
        self.router.post(
            "/",
            response_model=UserInDB,
            summary="Create new user",
            description="Admin only: Create a new user"
        )(self.create_user)

        # Reset user password
        self.router.post(
            "/{user_id}/reset",
            response_model=DefaultResponse,
            summary="Reset user password",
            description="Admin only: Reset user password and send new credentials via email"
        )(self.reset_user)

    async def get_users(
        self,
        userinfo=Depends(user_check),
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100)
    ) -> List[UserInDB]:
        """
        Get list of all users with pagination.
        Admins see all users; regular users only see users in shared projects.
        """
        if userinfo.is_admin:
            return Users.get_all_users(skip=skip, limit=limit)
        else:
            # Only return users who share at least one project with this user
            return Projects.get_users_in_shared_projects(userinfo.id)

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

    def generate_random_password(self, length=12):
        """Generate a cryptographically secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    async def create_user(
        self,
        user_data: UserCreate = Body(...),
        admin=Depends(admin_user_check)
    ) -> UserInDB:
        """
        Create a new user (Admin only)
        """
        # Check if email already exists
        if Users.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Generate random password
        password = self.generate_random_password()

        # Create user with the generated password
        new_user = Users.insert_new_user(
            username=user_data.email,
            password=password,
            role=user_data.role,
            name=user_data.full_name
        )
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user"
            )

        # Send email with credentials
        try:
            EmailService.send_new_user_credentials(
                username=new_user.username,
                password=password
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error sending email: {str(e)}")

        return new_user

    async def reset_user(
        self,
        user_id: str = Path(..., title="The ID of the user to reset password"),
        admin=Depends(admin_user_check)
    ) -> DefaultResponse:
        """
        Reset user password and send new credentials via email
        """
        # Check if user exists
        user = Users.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Generate new random password
        new_password = self.generate_random_password()

        # Update user with new password
        updated_user = Users.update_user_by_id(
            user_id,
            {"password": new_password}
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error resetting password"
            )

        # Send email with new credentials
        try:
            EmailService.send_new_user_credentials(
                username=user.username,
                password=new_password
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error sending reset email: {str(e)}")

        return DefaultResponse(code=200, result="Password reset successfully and sent via email")
