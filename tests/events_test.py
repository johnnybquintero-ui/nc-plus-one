from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_events_returns_200():
    response = client.get("/api/events")
    assert response.status_code == 200

def test_get_events_returns_10_items():
    response = client.get("/api/events")
    assert len(response.json()["events"]) == 10

def test_get_events_returns_in_date_order():
    response = client.get("/api/events")

    events = response.json()["events"]

    starts_at_values = [event["starts_at"] for event in events]
    assert starts_at_values == sorted(starts_at_values)

def test_get_events_returns_array_with_events_key():
    response = client.get("/api/events")

    assert isinstance(response.json(), dict)

    assert "events" in response.json()

    assert isinstance(response.json()["events"], list)