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

def test_get_event_returns_single_matched_event():
    event_id = 1
    response = client.get(f"/api/events/{event_id}")

    assert response.json()["event"]["id"] == 1

def test_get_event_returns_an_object_with_an_event_key():
    event_id = 1
    response = client.get(f"/api/events/{event_id}")

    assert "event" in response.json()
    assert isinstance(response.json(), object)

def test_get_event_not_found_returns_404():
    event_id = 9999999
    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "NOT_FOUND"

def test_get_event_has_venue_details():
    event_id = 1
    response = client.get(f"/api/events/{event_id}")

    assert response.json()["event"]["location"] == "Nexus, University of Leeds"
    assert response.json()["event"]["address"] == "Discovery Way, Leeds, LS2 3AA"
    assert response.json()["event"]["capacity"] == 200

def test_get_event_returns_422_if_id_is_not_int():
    event_id = "one"
    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 422