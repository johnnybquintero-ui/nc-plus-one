from fastapi.testclient import TestClient
from main import app
import pytest
from src.auth import hash_password, create_access_token
from db.connection import get_connection
from uuid import uuid4

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_user():
    """
    Create a temporary user for a test and remove it afterwards.
    """

    password = "password123"
    email = f"johnny-{uuid4()}@example.com"
    user_id = None

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password, name)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (
                        email,
                        hash_password(password),
                        "Johnny Quintero",
                    ),
                )

                user_id = cur.fetchone()["id"]

            conn.commit()

        yield {
            "id": user_id,
            "email": email,
            "password": password,
            "name": "Johnny Quintero",
        }

    finally:
        if user_id is not None:
            with get_connection() as conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            DELETE FROM rsvps
                            WHERE attendee_id = %s
                               OR event_id IN (
                                   SELECT id
                                   FROM events
                                   WHERE organiser_id = %s
                               )
                            """,
                            (user_id, user_id),
                        )

                        cur.execute(
                            """
                            DELETE FROM events
                            WHERE organiser_id = %s
                            """,
                            (user_id,),
                        )

                        cur.execute(
                            """
                            DELETE FROM users
                            WHERE id = %s
                            """,
                            (user_id,),
                        )

                    conn.commit()

                except Exception:
                    conn.rollback()
                    raise

@pytest.fixture
def cleanup_users():
    """
    Track test user emails and delete them after the test.

    Tests can append created email addresses to the yielded list to ensure
    any temporary users are removed during teardown.
    """

    emails = []
    yield emails

    if emails:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM users WHERE email = ANY(%s)",
                    (emails,),
                )
                user_ids = [row["id"] for row in cur.fetchall()]

                if user_ids:
                    cur.execute(
                        "DELETE FROM rsvps WHERE attendee_id = ANY(%s)",
                        (user_ids,),
                    )

                cur.execute(
                    "DELETE FROM users WHERE email = ANY(%s)",
                    (emails,),
                )

                conn.commit()

@pytest.fixture
def auth_headers(sample_user):
    token = create_access_token(sample_user["id"])

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def sample_event(sample_user):
    """
    Create a temporary event owned by the temporary test user.
    """

    event = {
        "title": "Real Python demo for Junior Data Engineers",
        "description": (
            "A hands-on workshop introducing junior data engineers "
            "to Python fundamentals, APIs and PostgreSQL."
        ),
        "starts_at": "2026-10-10T09:00:00+01:00",
        "ends_at": "2026-10-10T17:00:00+01:00",
        "organiser_id": sample_user["id"],
        "venue_id": 2,
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (
                    title,
                    description,
                    starts_at,
                    ends_at,
                    organiser_id,
                    venue_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    event["title"],
                    event["description"],
                    event["starts_at"],
                    event["ends_at"],
                    event["organiser_id"],
                    event["venue_id"],
                ),
            )

            event["id"] = cur.fetchone()["id"]
            conn.commit()

    try:
        yield event
    finally:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM rsvps WHERE event_id = %s",
                    (event["id"],),
                )

                cur.execute(
                    "DELETE FROM events WHERE id = %s",
                    (event["id"],),
                )

                conn.commit()

@pytest.fixture
def attendee_user():
    password = "password123"
    email = f"attendee-{uuid4()}@example.com"
    user_id = None

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password, name)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (
                        email,
                        hash_password(password),
                        "Bob Jones",
                    ),
                )

                user_id = cur.fetchone()["id"]

            conn.commit()

        yield {
            "id": user_id,
            "email": email,
            "password": password,
            "name": "Bob Jones",
        }

    finally:
        if user_id is not None:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM rsvps WHERE attendee_id = %s",
                        (user_id,),
                    )

                    cur.execute(
                        "DELETE FROM users WHERE id = %s",
                        (user_id,),
                    )

                conn.commit()

@pytest.fixture
def sample_rsvp(sample_event, attendee_user):
    rsvp = {
        "attendee_id": attendee_user["id"],
        "event_id": sample_event["id"],
    }

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rsvps (
                    attendee_id,
                    event_id
                )
                VALUES (%s, %s)
                RETURNING
                    id,
                    attendee_id,
                    event_id,
                    created_at
                """,
                (
                    rsvp["attendee_id"],
                    rsvp["event_id"],
                ),
            )

            created_rsvp = cur.fetchone()

        conn.commit()

    try:
        yield created_rsvp

    finally:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM rsvps WHERE id = %s",
                    (created_rsvp["id"],),
                )

            conn.commit()