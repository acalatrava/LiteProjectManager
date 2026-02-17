from fastapi import Body, HTTPException, status
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.users import UserInDB, UserUpdate
from app.db.relational import Users
from app.services.authentication import user_check
from fastapi import Depends


class UserInfoEndpoint(BaseEndpoint):

    def __init__(self):
        super().__init__()

        # Routes
        self.router.get("/", response_model=UserInDB)(self.get)
        self.router.patch("/", response_model=UserInDB)(self.update)

    async def get(self, userinfo=Depends(user_check)) -> UserInDB:
        # Get the token from authentication bearer
        return userinfo

    async def update(
        self,
        user_update: UserUpdate = Body(...),
        userinfo=Depends(user_check)
    ) -> UserInDB:
        """Update the authenticated user's information"""
        update_data = user_update.model_dump(exclude_unset=True)

        # Prevent privilege escalation — users cannot change their own role
        if 'role' in update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change own role"
            )

        # Prevent user from deactivating their own account
        if 'is_active' in update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users cannot deactivate their own account"
            )

        if 'username' in update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username/email cannot be modified"
            )

        # If password change is requested, verify current password
        if 'new_password' in update_data:
            if 'current_password' not in update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required"
                )

            # Verify current password
            if not Users.verify_password(userinfo.username, update_data['current_password']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )

            # Replace new_password key with password for the update
            update_data['password'] = update_data.pop('new_password')
            update_data.pop('current_password')  # Remove current_password as it's not needed for update

        # Update user
        updated_user = Users.update_user_by_id(
            userinfo.id,
            update_data
        )

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user information"
            )

        return updated_user
