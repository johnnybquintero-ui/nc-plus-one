from fastapi.testclient import TestClient
from main import app
from src.auth import hash_password, verify_password, create_access_token, JWT_ALGORITHM, JWT_SECRET
import jwt

client = TestClient(app)

def test_verify_password_returns_true_for_matching_password():
    password = "password123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True

def test_verify_password_returns_false_for_incorrect_password():
    hashed = hash_password("password123")

    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token_contains_user_id():
    token = create_access_token(1)

    payload = jwt.decode(
    token,
    JWT_SECRET,
    algorithms=[JWT_ALGORITHM],
)
    assert payload["sub"] == "1"

def test_create_access_token_contains_expiry():
    token = create_access_token(1)

    payload = jwt.decode(
    token,
    JWT_SECRET,
    algorithms=[JWT_ALGORITHM],
)

    assert "exp" in payload

def test_login_user_verifies_submitted_password_against_stored_hash(client, sample_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": sample_user["email"],
            "password": sample_user["password"],
        },
    )

    assert response.status_code == 200

def test_login_user_returns_401_for_invalid_credentials_securely(client, sample_user):
        response = client.post(
        "/api/auth/login",
        json={
            "email": sample_user["email"],
            "password": "wrongpassword",
        },
    )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

def test_login_user_returns_422_Unprocessable_entity_if_missing_field(client, sample_user):
        response = client.post(
        "/api/auth/login",
        json={
            "email": sample_user["email"]
        },
    )

        assert response.status_code == 422
