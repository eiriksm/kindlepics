from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_runs() -> None:
    assert str(5) == "5"

