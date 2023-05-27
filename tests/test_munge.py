import pytest
from httpx import AsyncClient

from src.bean_counter.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_process_incoming():
    response = client.post("/process/incoming")
    assert response.status_code == 201
