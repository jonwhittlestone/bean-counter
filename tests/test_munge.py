import pytest
from httpx import AsyncClient

from src.bean_counter.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_process_inflow():
    response = client.post("/process/inflow")
    assert response.status_code == 201
    # assert response.json() == {"msg": "Hello World"}
