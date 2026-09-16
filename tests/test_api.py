from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_recommend_endpoint():
    response = client.post(
        "/recommend",
        json={
            "query": "precast concrete pipes",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "precast concrete pipes"
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert data["recommendations"][0]["standardNumber"] == (
        "IS 458:2021"
    )


def test_recommend_endpoint_rejects_empty_query():
    response = client.post(
        "/recommend",
        json={
            "query": "",
            "limit": 3,
        },
    )

    assert response.status_code == 422