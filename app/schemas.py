from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str # Partener, Advocate, Clerk, Accounts, Admin

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    created_at: datetime

    class Config: 
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None