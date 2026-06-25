from pydantic import BaseModel, EmailStr

class CredentialsRequest(BaseModel):
    email: EmailStr
    password: str