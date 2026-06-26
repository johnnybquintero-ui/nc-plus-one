from fastapi.testclient import TestClient
from main import app
from src.auth import hash_password, verify_password, create_access_token, get_user_by_email, JWT_ALGORITHM, JWT_SECRET
import jwt
import pytest
from db.connection import get_connection

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

def test_register_user_returns_201_and_created_user(client, cleanup_users):
    email = "newuser@new.com"
    cleanup_users.append(email)

    response = client.post(
         "/api/auth/register",
         json ={
              "name": "Newy McNewson",
              "email": email,
              "password": "newpassword123",
         },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "registered"
    assert body["name"] == "Newy McNewson"
    assert body["email"] == "newuser@new.com"


def test_register_user_stores_hashed_password(client, cleanup_users):
    email = "newuser@new.com"
    cleanup_users.append(email)

    response = client.post(
         "/api/auth/register",
         json ={
              "name": "Newy McNewson",
              "email": email,
              "password": "newpassword123",
         },
    )
    assert response.status_code == 201

    user = get_user_by_email(email)
    assert user["password"] != "newpassword123"

def test_register_user_response_does_not_include_password(client, cleanup_users):
    email = "newuser@new.com"
    cleanup_users.append(email)

    response = client.post(
         "/api/auth/register",
         json ={
              "name": "Newy McNewson",
              "email": email,
              "password": "newpassword123",
         },
    )

    assert "password" not in response.json()

def test_register_user_duplicate_email_returns_409(client, sample_user):
    response = client.post(
         "/api/auth/register",
         json ={
            "name": sample_user["name"],
            "email": sample_user["email"],
            "password": sample_user["password"],
         },
    )

    assert response.status_code == 409

# Parameterize this test so pytest executes it once for each payload
# instead of duplicating three nearly identical test functions.
@pytest.mark.parametrize(
    "payload",
    [
        {
            "email": "johnny@example.com",
            "password": "password123",
        },
        {
            "name": "Johnny Quintero",
            "password": "password123",
        },
        {
            "name": "Johnny Quintero",
            "email": "johnny@example.com",
        },
    ],
)
def test_register_user_missing_required_field_returns_422(client, payload):
    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 422