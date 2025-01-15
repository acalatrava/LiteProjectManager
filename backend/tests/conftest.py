import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import DB
from app.models.user import User
from app.models.sample import Sample
from app.models.auth_token import AuthToken
import os
import tempfile


@pytest.fixture(scope="session")
def test_db_path():
    # Create a temporary database file
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture(scope="session")
def test_db(test_db_path):
    # Override the database path
    import app.core.config as config
    config.SQLITE_PATH = test_db_path

    # Configure test database
    DB.init(test_db_path)
    DB.connect()

    # Create tables
    from app.models.project import Project, ProjectMember
    from app.models.task import Task
    DB.create_tables([User, Sample, AuthToken, Project, ProjectMember, Task])

    yield DB

    # Cleanup
    DB.close()


@pytest.fixture(scope="session")
def client(test_db):
    return TestClient(app)


@pytest.fixture(scope="session")
def admin_credentials():
    return {
        "username": "admin@test.com",
        "password": "adminpass123",
        "name": "Admin User"
    }


@pytest.fixture(scope="session")
def user_credentials():
    return {
        "username": "user@test.com",
        "password": "userpass123",
        "name": "Test User"
    }


@pytest.fixture(scope="session")
def admin_token(client, admin_credentials):
    # Try to login first
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": admin_credentials["username"],
            "password": admin_credentials["password"]
        }
    )

    if response.status_code == 401:
        # If login fails, create admin user
        response = client.post(
            "/signup",
            json=admin_credentials
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
    else:
        token = response.json()["access_token"]

    # Verify admin role
    verify_response = client.get(
        "/api/v1/userinfo/",
        headers={"Authorization": f"Bearer {token}"}
    )

    if verify_response.status_code == 200:
        user_info = verify_response.json()
        if user_info.get("role") != "admin":
            # Update user to admin role using direct database access
            from app.models.user import User, UserRole
            User.update(role=UserRole.ADMIN.value).where(
                User.username == admin_credentials["username"]
            ).execute()

            # Get new token after role update
            response = client.post(
                "/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "password",
                    "username": admin_credentials["username"],
                    "password": admin_credentials["password"]
                }
            )
            assert response.status_code == 200
            token = response.json()["access_token"]

    return token


@pytest.fixture(scope="session")
def user_token(client, user_credentials):
    # Try to login first
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user_credentials["username"],
            "password": user_credentials["password"]
        }
    )

    if response.status_code == 401:
        # If login fails, create user
        response = client.post(
            "/signup",
            json=user_credentials
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
    else:
        token = response.json()["access_token"]

    # Verify user role
    verify_response = client.get(
        "/api/v1/userinfo/",
        headers={"Authorization": f"Bearer {token}"}
    )

    if verify_response.status_code == 200:
        user_info = verify_response.json()
        if user_info.get("role") != "user":
            # Update user to regular user role using direct database access
            from app.models.user import User, UserRole
            User.update(role=UserRole.USER.value).where(
                User.username == user_credentials["username"]
            ).execute()

            # Get new token after role update
            response = client.post(
                "/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "password",
                    "username": user_credentials["username"],
                    "password": user_credentials["password"]
                }
            )
            assert response.status_code == 200
            token = response.json()["access_token"]

    return token
