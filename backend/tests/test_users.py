import pytest
from fastapi.testclient import TestClient


def test_get_users_admin(client: TestClient, admin_token):
    # First verify admin status
    verify_response = client.get(
        "/api/v1/userinfo/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert verify_response.json()["role"] == "admin"

    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0


def test_get_users_unauthorized(client: TestClient, user_token):
    # First verify user status
    verify_response = client.get(
        "/api/v1/userinfo/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert verify_response.json()["role"] == "user"

    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 401


def test_update_user(client: TestClient, admin_token, user_token):
    # First get a user to update
    response = client.get(
        "/api/v1/userinfo/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    user_id = response.json()["id"]

    # Update user
    response = client.patch(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Updated Name"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_user(client: TestClient, admin_token, user_token):
    # First get a user to delete
    response = client.get(
        "/api/v1/userinfo/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Delete user
    response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

    # Verify user is deleted
    response = client.get(
        "/api/v1/userinfo/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 401  # Token should be invalid after user deletion
