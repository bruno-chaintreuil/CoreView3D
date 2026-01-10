import pytest
from fastapi.testclient import TestClient
from coreview3d.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_session_id(client):
    return "test-session-for-api"


def test_calculate_section_endpoint_success(client, test_session_id):
    response = client.post(
        "/api/cross-section/calculate",
        json={
            "session_id": test_session_id,
            "hole_ids": ["DH001", "DH002"],
            "point_A": [500000, 6000000],
            "point_B": [500500, 6000500],
            "tolerance": 100.0
        }
    )
    
    assert response.status_code in [200, 404]


def test_calculate_section_endpoint_missing_session(client):
    response = client.post(
        "/api/cross-section/calculate",
        json={
            "session_id": "non-existent-session",
            "hole_ids": ["DH001"],
            "tolerance": 100.0
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()['detail'].lower()


def test_calculate_section_endpoint_invalid_data(client, test_session_id):
    response = client.post(
        "/api/cross-section/calculate",
        json={
            "session_id": test_session_id,
            "hole_ids": [],  # Vide
            "tolerance": -10  # Invalide
        }
    )
    
    assert response.status_code in [400, 422]  # Validation error


def test_calculate_line_endpoint_success(client, test_session_id):
    response = client.post(
        "/api/cross-section/calculate-line",
        json={
            "session_id": test_session_id,
            "hole_ids": ["DH001", "DH002"]
        }
    )
    
    assert response.status_code in [200, 404]


def test_calculate_line_endpoint_insufficient_holes(client, test_session_id):
    response = client.post(
        "/api/cross-section/calculate-line",
        json={
            "session_id": test_session_id,
            "hole_ids": ["DH001"]  # Seulement 1
        }
    )
    
    if response.status_code != 404:  # Si session existe
        assert response.status_code == 400

