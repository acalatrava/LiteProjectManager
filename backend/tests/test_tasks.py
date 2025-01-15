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

    return project


def create_test_task(client: TestClient, admin_token, project_id: str):
    response = client.post(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Task",
            "description": "A test task",
            "project_id": project_id,
            "start_date": (datetime.now()).isoformat(),
            "deadline": (datetime.now() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == 200
    return response.json()


def test_create_task(client: TestClient, admin_token):
    # First create a project
    project = create_test_project(client, admin_token)

    # Create task
    response = client.post(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Task",
            "description": "A test task",
            "project_id": project["id"],
            "start_date": (datetime.now()).isoformat(),
            "deadline": (datetime.now() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == "pending"


def test_get_tasks(client: TestClient, admin_token):
    # First create a project
    project = create_test_project(client, admin_token)

    # Create a task
    task = create_test_task(client, admin_token, project["id"])

    # Get all tasks
    response = client.get(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) > 0
    assert any(t["id"] == task["id"] for t in tasks)


def test_update_task(client: TestClient, admin_token):
    # First create a project and task
    project = create_test_project(client, admin_token)
    task = create_test_task(client, admin_token, project["id"])

    # Update task
    new_deadline = (datetime.now() + timedelta(days=14)).isoformat()
    response = client.put(
        f"/api/v1/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Updated Task",
            "description": "An updated test task",
            "project_id": task["project_id"],
            "start_date": task["start_date"],
            "deadline": new_deadline,
            "status": "in_progress"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Task"
    assert data["status"] == "in_progress"


def test_delete_task(client: TestClient, admin_token):
    # First create a project and task
    project = create_test_project(client, admin_token)
    task = create_test_task(client, admin_token, project["id"])

    # Delete task
    response = client.delete(
        f"/api/v1/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

    # Verify task is deleted
    response = client.get(
        "/api/v1/tasks/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    tasks = response.json()
    assert not any(t["id"] == task["id"] for t in tasks)


def test_gantt_chart(client: TestClient, admin_token):
    # First create a project with tasks
    project = create_test_project(client, admin_token)

    # Create multiple tasks
    tasks = []
    for i in range(3):
        task = create_test_task(client, admin_token, project["id"])
        tasks.append(task)

    # Get Gantt chart
    response = client.get(
        f"/api/v1/gantt/{project['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == len(tasks)

    # Verify task data in Gantt chart
    for task in data["tasks"]:
        assert "id" in task
        assert "name" in task
        assert "start" in task
        assert "end" in task
        assert "progress" in task
        assert task["progress"] in [0.0, 0.5, 1.0]
