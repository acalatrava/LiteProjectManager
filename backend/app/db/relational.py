from datetime import datetime, timedelta
import hashlib
import re
import uuid
from typing import List, Optional
from playhouse.shortcuts import model_to_dict

from app.models.user import User
from app.models.sample import Sample
from app.schemas.users import UserRole, UserInDB
from app.schemas.sample import SampleModel
from .database import DB, get_db
from app.models.auth_token import AuthToken
from app.core.config import AUTH_TOKEN_LIFETIME


class SampleTable:
    def __init__(self):
        with get_db():
            DB.create_tables([Sample])

    def delete_data_by_id(self, id: str) -> bool:
        try:
            query = Sample.delete().where(Sample.id == id)
            query.execute()

            return True
        except:
            return False

    def delete_all_data(self) -> bool:
        try:
            query = Sample.delete()
            query.execute()

            return True
        except:
            return False

    def delete_specific_data(self, info: str) -> bool:
        try:
            query = Sample.delete().where(Sample.info == info)
            query.execute()

            return True
        except:
            return False

    def delete_data_by_date(self, date: datetime) -> bool:
        try:
            query = Sample.delete().where(Sample.date == date)
            query.execute()

            return True
        except:
            return False

    def insert_new_data(
        self, info: str
    ) -> Optional[SampleModel]:
        # Create new data with a UUID as string ID
        sample_id = str(uuid.uuid4())
        Sample.create(
            id=sample_id,
            date=datetime.now(),
            info=info
        )
        return SampleModel(
            id=sample_id,
            date=datetime.now(),
            info=info
        )

    def get_all_data(self, skip: int = 0, limit: int = 50) -> List[SampleModel]:
        return [
            SampleModel(id=str(sample.id), date=sample.date, info=sample.info)
            for sample in Sample.select().limit(limit).offset(skip)
        ]

    def search_samples(self, query: str, skip: int = 0, limit: int = 50) -> List[SampleModel]:
        # Case-insensitive search in the info field
        return [
            SampleModel(id=str(sample.id), date=sample.date, info=sample.info)
            for sample in Sample.select()
            .where(Sample.info.contains(query))
            .limit(limit)
            .offset(skip)
        ]


class UsersTable:
    def __init__(self):
        with get_db():
            DB.create_tables([User, AuthToken])

    def insert_new_user(
        self, username: str, password: str, role: str = UserRole.USER.value, name: str = ''
    ) -> Optional[UserInDB]:
        # Set username to lowercase
        username = username.lower()

        # Check username is a valid email using regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
            return None

        # Check if the username already exists
        if self.get_user_by_username(username):
            return None

        try:
            # Generate a random salt
            salt = str(uuid.uuid4())

            # Encrypt the password using sha256 and the salt
            password = hashlib.sha256((salt + password).encode()).hexdigest()

            # Generate an id from the username
            id = str(uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=username.lower()))

            # Generate a token based on id and random string
            token = hashlib.sha256((id + str(uuid.uuid4())).encode()).hexdigest()

            # Check if this is the first user
            is_first_user = self.get_num_users() == 0

            # Create new user with admin role if it's the first user
            user = User.create(
                id=id,
                token=token,
                username=username.lower(),
                password=password,
                salt=salt,
                role=UserRole.ADMIN.value if is_first_user else UserRole.USER.value,
                name=name,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            return UserInDB(**user.to_dict())
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_user_by_id(self, id: str) -> Optional[UserInDB]:
        try:
            user = User.get(User.id == id)
            return UserInDB(**user.to_dict())
        except User.DoesNotExist:
            return None

    def get_user_by_token(self, token: str) -> Optional[UserInDB]:
        try:
            # Get valid token
            auth_token = (AuthToken
                          .select()
                          .where(
                              (AuthToken.token == token) &
                              (AuthToken.is_active == True) &
                              (AuthToken.expires_at > datetime.now())
                          )
                          .first())

            if not auth_token:
                return None

            user = User.get(User.id == auth_token.user_id)
            return UserInDB(**user.to_dict())
        except Exception as e:
            print(f"Error getting user by token: {e}")
            return None

    def is_admin(self, token: str) -> bool:
        # Get user by token
        user = self.get_user_by_token(token)
        return user.role == UserRole.ADMIN.value

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        try:
            user = User.get(User.username == username.lower())
            return UserInDB(**user.to_dict())
        except:
            return None

    def get_user_by_username_and_password(self, username: str, password: str) -> Optional[tuple[UserInDB, str]]:
        # Set username to lowercase
        username = username.lower()

        # Check username format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
            return None

        try:
            # Get user and verify password
            user = User.get(User.username == username.lower())
            hashed_password = hashlib.sha256((user.salt + password).encode()).hexdigest()

            if user.password != hashed_password:
                return None

            # Create new auth token
            token = self.create_auth_token(user.id)
            if not token:
                return None

            return UserInDB(**user.to_dict()), token

        except Exception as e:
            return None

    def get_users(self, skip: int = 0, limit: int = 50) -> List[UserInDB]:
        return [
            UserInDB.model_validate(user)
            for user in User.select().limit(limit).offset(skip)
        ]

    def get_num_users(self) -> Optional[int]:
        return User.select().count()

    def update_user_role_by_id(self, id: str, role: str) -> Optional[UserInDB]:
        try:
            query = User.update(role=role).where(User.id == id)
            query.execute()

            user = User.get(User.id == id)
            return UserInDB(**model_to_dict(user))
        except:
            return None

    def update_user_by_id(self, id: str, updated: dict) -> Optional[UserInDB]:
        try:
            query = User.update(**updated).where(User.id == id)
            query.execute()

            user = User.get(User.id == id)
            return UserInDB.model_validate(user)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    def delete_user_by_id(self, id: str) -> bool:
        try:
            # Delete associated auth tokens first
            AuthToken.delete().where(AuthToken.user_id == id).execute()

            # Then delete the user
            query = User.delete().where(User.id == id)
            query.execute()

            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def update_user_role(self, user_id: str, new_role: UserRole) -> Optional[UserInDB]:
        try:
            user = User.get(User.id == user_id)
            user.role = new_role
            user.updated_at = datetime.now()
            user.save()
            return UserInDB(**user.to_dict())
        except User.DoesNotExist:
            return None

    def get_active_users(self, skip: int = 0, limit: int = 50) -> List[UserInDB]:
        return [
            UserInDB.model_validate(user)
            for user in User.select()
            .where(User.is_active == True)
            .limit(limit)
            .offset(skip)
        ]

    def get_all_users(self, skip: int = 0, limit: int = 50) -> List[UserInDB]:
        return [
            UserInDB.model_validate(user)
            for user in User.select().limit(limit).offset(skip)
        ]

    def verify_password(self, username: str, password: str) -> bool:
        try:
            user = User.get(User.username == username.lower())
            # Encrypt the password using sha256 and the user's salt
            hashed_password = hashlib.sha256((user.salt + password).encode()).hexdigest()
            return user.password == hashed_password
        except User.DoesNotExist:
            return False

    def create_auth_token(self, user_id: str) -> Optional[str]:
        try:
            # Generate new token
            token = hashlib.sha256((str(uuid.uuid4()) + str(datetime.now())).encode()).hexdigest()

            # Calculate expiration
            expires_at = datetime.now() + timedelta(seconds=int(AUTH_TOKEN_LIFETIME))

            # Create token record
            AuthToken.create(
                id=str(uuid.uuid4()),
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )

            return token
        except Exception as e:
            print(f"Error creating auth token: {e}")
            return None


Users = UsersTable()
Samples = SampleTable()
