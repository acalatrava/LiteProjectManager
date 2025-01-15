from fastapi.testclient import TestClient


def test_add_sample(client: TestClient, user_token):
    response = client.post(
        "/api/v1/sample/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"info": "Test sample data"}
    )
    assert response.status_code == 200
    assert response.json()["result"] == "Data added successfully"


def test_get_samples(client: TestClient, user_token):
    # First add a sample
    client.post(
        "/api/v1/sample/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"info": "Test sample data"}
    )

    # Get samples
    response = client.get(
        "/api/v1/sample/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0


def test_delete_sample(client: TestClient, user_token):
    # First add a sample
    client.post(
        "/api/v1/sample/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"info": "Test sample to delete"}
    )

    # Get the sample ID
    response = client.get(
        "/api/v1/sample/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    sample_id = response.json()["results"][0]["id"]

    # Delete the sample
    response = client.delete(
        f"/api/v1/sample/{sample_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["result"] == "Data deleted successfully"
