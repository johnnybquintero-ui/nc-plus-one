from fastapi.testclient import TestClient
from main import app
import pytest
from src.auth import hash_password
from db.connection import get_connection

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_user():
    """
    Create a temporary user in the test database.

    Yields the user's id, email and plain-text password for use in
    authentication tests, then removes the user after the test completes.
    """

    conn = get_connection()
    cur = conn.cursor()

    password = "password123"

    cur.execute(
        """
        INSERT INTO users (email, password, name)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        ("johnny@example.com", hash_password(password), "Johnny Quintero"),
    )

    user_id = cur.fetchone()["id"]
    conn.commit()

    yield {
        "id": user_id,
        "email": "johnny@example.com",
        "password": password,
        "name": "Johnny Quintero",
    }

    cur.execute(
        "DELETE FROM users WHERE id = %s",
        (user_id,)
    )
    conn.commit()

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
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM users WHERE email = ANY(%s)",
            (emails,),
        )

        conn.commit()
        cur.close()
        conn.close()
