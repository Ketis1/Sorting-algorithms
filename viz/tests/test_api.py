import pytest
from fastapi.testclient import TestClient

from backend.discovery import clear_algorithm_cache
from backend.main import app


@pytest.fixture(autouse=True)
def reset_discovery_cache():
    clear_algorithm_cache()
    yield
    clear_algorithm_cache()


@pytest.fixture
def client():
    return TestClient(app)


def test_list_algorithms(client):
    response = client.get("/api/algorithms")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert any(item["id"] == "bubble_sort" for item in payload)


def test_sort_bubble_sort(client):
    response = client.post(
        "/api/sort",
        json={"algorithm": "bubble_sort", "array": [5, 3, 8, 1, 2]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"] == [1, 2, 3, 5, 8]


def test_sort_rejects_invalid_algorithm_id(client):
    response = client.post(
        "/api/sort",
        json={"algorithm": "../bubble_sort", "array": [1, 2, 3]},
    )
    assert response.status_code == 400
    assert "Invalid algorithm id" in response.json()["detail"]


def test_sort_rejects_unknown_algorithm(client):
    response = client.post(
        "/api/sort",
        json={"algorithm": "missing_sort", "array": [1, 2, 3]},
    )
    assert response.status_code == 404
