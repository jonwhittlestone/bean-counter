import pytest
from httpx import AsyncClient

from starlette.status import HTTP_200_OK
from src.bean_counter.main import SheetVersionEnum, app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_summary():
    response = client.get("/summary")
    assert response.status_code == HTTP_200_OK
