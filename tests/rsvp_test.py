from fastapi.testclient import TestClient
from main import app

def test_create_rsvp_responds_with_201_and_rsvp(client, sample_event, sample_user, auth_headers):
    response = client.post(
    f"/api/events/{sample_event['id']}/rsvp", headers = auth_headers)

    assert response.status_code == 201

    body = response.json()
    rsvp = body["rsvp"]

    assert rsvp["attendee_id"] == sample_user["id"]
    assert rsvp["event_id"] == sample_event["id"]
    assert "id" in rsvp
    assert "created_at" in rsvp

def test_create_rsvp_responds_with_401_if_token_invalid(client, sample_event):
    response = client.post(
        f"/api/events/{sample_event['id']}/rsvp", headers = {"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401

def test_create_rsvp_responds_with_404_if_event_does_not_exist(client, auth_headers):
    response = client.post("/api/events/99999/rsvp", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "Event not found"
    assert response.json()["detail"]["code"] == "NOT_FOUND"

def test_create_rsvp_responds_with_409_if_user_has_already_rsvped(
    client,
    sample_event,
    auth_headers,
):
    # First RSVP succeeds
    response = client.post(
        f"/api/events/{sample_event['id']}/rsvp",
        headers=auth_headers,
    )

    assert response.status_code == 201

    # Second RSVP for the same event by the same user
    response = client.post(
        f"/api/events/{sample_event['id']}/rsvp",
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"]["message"] == "User has already RSVPed to this event"
    assert response.json()["detail"]["code"] == "CONFLICT"

def test_create_rsvp_responds_with_401_if_token_missing(
    client,
    sample_event,
):
    response = client.post(
        f"/api/events/{sample_event['id']}/rsvp"
    )

    assert response.status_code == 401

def test_delete_rsvp_responds_with_204_on_success(
    client,
    sample_event,
    auth_headers,
):
    client.post(
    f"/api/events/{sample_event['id']}/rsvp",
    headers=auth_headers,
)
    response = client.delete(
    f"/api/events/{sample_event['id']}/rsvp/me",
    headers=auth_headers,   
    )
    assert response.status_code == 204

def test_delete_rsvp_returns_401_without_valid_token(
    client,
    sample_event,
):
    response = client.delete(
    f"/api/events/{sample_event['id']}/rsvp/me",
    headers={
            "Authorization": "Bearer not-a-real-token"
        },   
    )
    assert response.status_code == 401

def test_delete_rsvp_responds_with_404_if_rsvp_does_not_exist(
    client,
    sample_event,
    auth_headers,
):
    response = client.delete(
    f"/api/events/{sample_event['id']}/rsvp/me",
    headers=auth_headers,   
    )
    assert response.status_code == 404