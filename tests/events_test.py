from db.connection import get_connection

def test_get_events_returns_200(client):
    response = client.get("/api/events")
    assert response.status_code == 200

def test_get_events_returns_10_items(client):
    response = client.get("/api/events")
    assert len(response.json()["events"]) == 10

def test_get_events_returns_in_date_order(client):
    response = client.get("/api/events")

    events = response.json()["events"]

    starts_at_values = [event["starts_at"] for event in events]
    assert starts_at_values == sorted(starts_at_values)

def test_get_events_returns_array_with_events_key(client):
    response = client.get("/api/events")

    assert isinstance(response.json(), dict)

    assert "events" in response.json()

    assert isinstance(response.json()["events"], list)

def test_get_event_returns_single_matched_event(client):
    event_id = 1
    response = client.get(f"/api/events/{event_id}")

    assert response.json()["event"]["id"] == 1

def test_get_event_returns_an_object_with_an_event_key(client):
    event_id = 1
    response = client.get(f"/api/events/{event_id}")

    assert "event" in response.json()
    assert isinstance(response.json(), object)

def test_get_event_not_found_returns_404(client):
    event_id = 9999999
    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "NOT_FOUND"

def test_get_event_has_venue_details(client):
    event_id = 1
    response = client.get(f"/api/events/{event_id}")

    assert response.json()["event"]["location"] == "Nexus, University of Leeds"
    assert response.json()["event"]["address"] == "Discovery Way, Leeds, LS2 3AA"
    assert response.json()["event"]["capacity"] == 200

def test_get_event_returns_422_if_id_is_not_int(client):
    event_id = "one"
    response = client.get(f"/api/events/{event_id}")

    assert response.status_code == 422

def test_create_event_returns_with_201_and_created_event(
    client,
    sample_user,
    auth_headers,
):
    new_event = {
        "title": "Summer Rooftop Social",
        "description": "An evening of networking and good vibes.",
        "starts_at": "2026-08-15T18:00:00Z",
        "ends_at": "2026-08-15T21:00:00Z",
        "venue_id": 2,
    }

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json=new_event,
    )

    assert response.status_code == 201

    event = response.json()["event"]

    assert event["title"] == new_event["title"]
    assert event["description"] == new_event["description"]
    assert event["venue_id"] == new_event["venue_id"]
    assert event["organiser_id"] == sample_user["id"]
    assert "id" in event
    assert "created_at" in event

def test_create_event_derives_organiser_id_from_token(
    client,
    sample_user,
    auth_headers,
):
    new_event = {
        "title": "Token Ownership Test",
        "description": "Testing that organiser_id comes from the JWT.",
        "starts_at": "2026-08-15T18:00:00Z",
        "ends_at": "2026-08-15T21:00:00Z",
        "venue_id": 2,
        "organiser_id": 9999,
    }

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json=new_event,
    )

    assert response.status_code == 201

    event = response.json()["event"]

    assert event["organiser_id"] == sample_user["id"]
    assert event["organiser_id"] != new_event["organiser_id"]

def test_create_event_returns_401_without_valid_token(
    client,
    auth_headers,
):
    new_event = {
            "title": "Invalid Token Test",
            "description": "Testing that invalid token returns 401",
            "starts_at": "2026-08-15T18:00:00Z",
            "ends_at": "2026-08-15T21:00:00Z",
            "venue_id": 2,
            "organiser_id": 1,
        }
    
    response = client.post(
        "/api/events",
        headers={
            "Authorization": "Bearer not-a-real-token"
        },
        json=new_event,
    )
    
    assert response.status_code == 401

def test_create_event_returns_400_with_malformed_fields(
    client,
    auth_headers,
):
    new_event = {
        "title": 1234,
        "description": 5678,
        "starts_at": "NOT A TIME!",
        "ends_at": "NOT A TIME!",
        "venue_id": "DAVID",
        "organiser_id": "BRENT",
    }

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json=new_event,
    )

    assert response.status_code == 400

def test_create_event_returns_400_with_missing_fields(
    client,
    auth_headers,
):
    new_event = {}

    response = client.post(
        "/api/events",
        headers=auth_headers,
        json=new_event,
    )

    assert response.status_code == 400