from fastapi.testclient import TestClient
import pytest


def test_signup(client: TestClient):
    response = client.post(
        "/signup",
        json={
            "username": "newuser@test.com",
            "password": "testpass123",
            "name": "New User"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_signup_invalid_email(client: TestClient):
    response = client.post(
        "/signup",
        json={
            "username": "invalid-email",
            "password": "testpass123",
            "name": "Invalid User"
        }
    )
    assert response.status_code == 400


def test_login_success(client: TestClient):
    # First create a user
    signup_response = client.post(
        "/signup",
        json={
            "username": "login@test.com",
            "password": "testpass123",
            "name": "Login User"
        }
    )
    assert signup_response.status_code == 200

    # Try logging in
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": "login@test.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": "login@test.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
