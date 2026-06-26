from pydantic import BaseModel, EmailStr

class CredentialsRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterCredentials(BaseModel):
    name: str
    email: EmailStr
    password: str