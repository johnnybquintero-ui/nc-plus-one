import os
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer

from src.schemas import CredentialsRequest, RegisterCredentials
from db.connection import get_connection

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 30

router = APIRouter()

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed.encode())

def create_access_token(user_id: int)->str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_user_by_email(email):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,),
        )
        return cur.fetchone()

@router.post("/api/auth/login")
def login_user(payload:CredentialsRequest):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, password FROM users WHERE email = %s",
            (payload.email,),
        )
        row = cur.fetchone()
        print(row)
        print(type(row))
        if row is None or not verify_password(payload.password, row["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = create_access_token(row["id"])
        return {"access_token": token, "token_type": "bearer"}
    
@router.post("/api/auth/register", status_code = 201)
def register_user(payload:RegisterCredentials):
    existing_user = get_user_by_email(payload.email)

    if existing_user:
        raise HTTPException(
            status_code = 409,
            detail ={"message": "Email already in use"}
        )

    conn = get_connection()
    with conn.cursor() as cur:
        hashed_password = hash_password(payload.password)
        cur.execute("INSERT INTO users(name, email, password) VALUES (%s, %s, %s) RETURNING id",(payload.name, payload.email, hashed_password))

        new_id = cur.fetchone()["id"]
        conn.commit()
        return {"user_id": new_id, "name": payload.name, "email": payload.email, "status": "registered"}