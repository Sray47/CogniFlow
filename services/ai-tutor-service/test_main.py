import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_ai_chat():
    r = client.post("/ai/chat", json={"user_id": "u1", "message": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert "AI: You said" in data["response"]
    assert data["history"]

def test_spaced_repetition():
    r = client.post("/ai/spaced-repetition", json={"user_id": "u1", "item_id": "item1", "performance": "easy"})
    assert r.status_code == 200
    data = r.json()
    assert data["next_review"] == "tomorrow"
    assert data["schedule"]

def test_adaptive_content():
    r = client.post("/ai/adaptive-content", json={"user_id": "u1", "topic": "math"})
    assert r.status_code == 200
    data = r.json()
    assert "math" in data["suggestions"][0]
