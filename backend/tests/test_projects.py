from fastapi.testclient import TestClient
from datetime import datetime, timedelta


def create_test_project(client: TestClient, admin_token):
    response = client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Project",
            "description": "A test project",
            "start_date": (datetime.now()).isoformat(),
            "deadline": (datetime.now() + timedelta(days=30)).isoformat()
        }
    )
    assert response.status_code == 200
    project = response.json()

    # Verify that the creator is a project manager
    response = client.get(
        f"/api/v1/projects/{project['id']}/members",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    members = response.json()
    assert any(m["role"] == "project_manager" for m in members)

    return project  # This return is OK as it's not a test function


def test_create_project(client: TestClient, admin_token):
    response = client.post(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Project",
            "description": "A test project",
            "start_date": (datetime.now()).isoformat(),
            "deadline": (datetime.now() + timedelta(days=30)).isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == "pending"


def test_get_projects(client: TestClient, admin_token):
    # First create a project
    project = create_test_project(client, admin_token)

    # Get all projects
    response = client.get(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    assert len(projects) > 0
    assert any(p["id"] == project["id"] for p in projects)


def test_update_project(client: TestClient, admin_token):
    # First create a project
    project = create_test_project(client, admin_token)

    # Update project
    new_deadline = (datetime.now() + timedelta(days=60)).isoformat()
    response = client.put(
        f"/api/v1/projects/{project['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Updated Project",
            "description": "An updated test project",
            "start_date": project["start_date"],
            "deadline": new_deadline,
            "status": "in_progress"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["status"] == "in_progress"


def test_delete_project(client: TestClient, admin_token):
    # First create a project
    project = create_test_project(client, admin_token)

    # Delete project
    response = client.delete(
        f"/api/v1/projects/{project['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

    # Verify project is deleted
    response = client.get(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    projects = response.json()
    assert not any(p["id"] == project["id"] for p in projects)
