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
    }

    cur.execute(
        "DELETE FROM users WHERE id = %s",
        (user_id,)
    )
    conn.commit()