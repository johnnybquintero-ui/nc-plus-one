from pydantic import BaseModel, EmailStr
from datetime import datetime

class CredentialsRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterCredentials(BaseModel):
    name: str
    email: EmailStr
    password: str

class CreateEventRequest(BaseModel):
    title: str
    description: str
    starts_at: datetime
    ends_at: datetime
    venue_id: int

class UpdateEventRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    venue_id: int | None = None