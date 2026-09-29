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

class ClientCreate(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    client_type: str = "Individual"  

class ClientResponse(BaseModel):
    id: int
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    client_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class MatterCreate(BaseModel):
    matter_number: str
    title: str
    practice_area: str  
    client_id: int
    assigned_advocate_id: int | None = None

class MatterResponse(BaseModel):
    id: int
    matter_number: str
    title: str
    practice_area: str
    status: str
    client_id: int
    assigned_advocate_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime
    priority: str = "Normal"  
    matter_id: int
    assigned_to_id: int | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    due_date: datetime
    status: str
    priority: str
    matter_id: int
    assigned_to_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True