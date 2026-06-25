import os
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer

from src.schemas import CredentialsRequest
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