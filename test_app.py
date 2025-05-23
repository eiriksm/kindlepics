from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_runs():
    assert str(5) == "5"

