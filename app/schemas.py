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

class InvoiceCreate(BaseModel):
    invoice_number: str
    matter_id: int
    amount: float
    due_date: datetime

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    matter_id: int
    amount: float
    status: str
    due_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str | None = None
    file_size: int | None = None
    matter_id: int
    uploaded_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TimeEntryCreate(BaseModel):
    description: str
    hours: float
    is_billable: bool = True
    matter_id: int
    date_performed: datetime | None = None

class TimeEntryResponse(BaseModel):
    id: int
    description: str
    hours: float
    hourly_rate: float
    total_amount: float
    is_billable: bool
    is_billed: bool
    date_performed: datetime
    matter_id: int
    user_id: int
    invoice_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class InvoiceFromTimeEntriesCreate(BaseModel):
    invoice_number: str
    matter_id: int
    due_date: datetime
    time_entry_ids: list[int]

class EventCreate(BaseModel):
    title: str
    description: str | None = None
    event_type: str  # Court Hearing, Client Meeting, Filing Deadline, Limitation Period
    location: str | None = None
    start_time: datetime
    end_time: datetime
    matter_id: int
    assigned_to_id: int | None = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    event_type: str
    location: str | None = None
    start_time: datetime
    end_time: datetime
    matter_id: int
    created_by_id: int
    assigned_to_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True