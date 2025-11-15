"""
API Tests for the Ingest Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app import app
from api.dependencies import get_ingest_telemetry_use_case

# Create a test client
client = TestClient(app)

# Mock the use case
mock_ingest_use_case = AsyncMock()

def override_get_ingest_telemetry_use_case():
    return mock_ingest_use_case

app.dependency_overrides[get_ingest_telemetry_use_case] = override_get_ingest_telemetry_use_case

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test"""
    mock_ingest_use_case.reset_mock()

def test_ingest_raw_success():
    """
    Test successful ingestion of a raw measurement.
    """
    # Arrange
    mock_ingest_use_case.execute_raw.return_value = {
        "status": "success",
        "machine_id": "test-machine",
    }
    payload = {
        "machine_id": "test-machine",
        "timestamp": "2025-11-15T10:00:00Z",
        "metrics": {"temp": 100.0, "vibration": 5.0},
    }

    # Act
    response = client.post("/ingest/raw", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["machine_id"] == "test-machine"
    mock_ingest_use_case.execute_raw.assert_awaited_once()

def test_ingest_raw_machine_not_found():
    """
    Test ingestion when the machine ID is not found.
    """
    # Arrange
    mock_ingest_use_case.execute_raw.side_effect = ValueError("Machine test-machine not found")
    payload = {
        "machine_id": "test-machine",
        "timestamp": "2025-11-15T10:00:00Z",
        "metrics": {"temp": 100.0},
    }

    # Act
    response = client.post("/ingest/raw", json=payload)

    # Assert
    assert response.status_code == 404
    assert "Machine test-machine not found" in response.json()["detail"]
    mock_ingest_use_case.execute_raw.assert_awaited_once()

def test_ingest_features_success():
    """
    Test successful ingestion of a feature vector.
    """
    # Arrange
    mock_ingest_use_case.execute_features.return_value = {
        "status": "success",
        "machine_id": "test-machine",
    }
    payload = {
        "machine_id": "test-machine",
        "timestamp": "2025-11-15T10:00:00Z",
        "features": {"mean_temp": 98.0, "std_vibration": 1.2},
    }

    # Act
    response = client.post("/ingest/features", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_ingest_use_case.execute_features.assert_awaited_once()
