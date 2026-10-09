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

class AuditLogResponse(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: int | None = None
    details: str | None = None
    ip_address: str | None = None
    user_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class CounterpartyCreate(BaseModel):
    name: str
    role: str
    matter_id: int

class CounterpartyResponse(BaseModel):
    id: int
    name: str
    role: str
    matter_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConflictMatch(BaseModel):
    match_type: str  # Client Name, Client Email, Counterparty, Matter Title
    entity_id: int
    matched_text: str
    matter_id: int | None = None
    details: str

class ConflictCheckRequest(BaseModel):
    search_query: str  # Name of individual, company, or entity to screen

class ConflictCheckResponse(BaseModel):
    search_query: str
    has_potential_conflict: bool
    total_matches: int
    matches: list[ConflictMatch]

class TrustDepositRequest(BaseModel):
    matter_id: int
    amount: float
    description: str

class ApplyTrustToInvoiceRequest(BaseModel):
    invoice_id: int
    amount: float

class TrustTransactionResponse(BaseModel):
    id: int
    trust_account_id: int
    transaction_type: str
    amount: float
    description: str
    invoice_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class TrustAccountResponse(BaseModel):
    id: int
    matter_id: int
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    category: str
    description: str
    amount: float
    is_reimbursable: bool = True
    matter_id: int
    expense_date: datetime | None = None

class ExpenseResponse(BaseModel):
    id: int
    category: str
    description: str
    amount: float
    is_reimbursable: bool
    is_billed: bool
    expense_date: datetime
    matter_id: int
    paid_by_id: int
    invoice_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class AttachExpensesToInvoiceRequest(BaseModel):
    invoice_id: int
    expense_ids: list[int]

class FinancialSummary(BaseModel):
    total_invoiced: float
    total_paid: float
    total_unpaid: float
    total_trust_balances: float

class AdvocatePerformance(BaseModel):
    advocate_id: int
    full_name: str
    total_hours_logged: float
    total_billable_amount: float

class MatterStatusSummary(BaseModel):
    total_matters: int
    open_matters: int
    closed_matters: int
    by_practice_area: dict[str, int]

class DashboardAnalyticsResponse(BaseModel):
    financials: FinancialSummary
    matter_stats: MatterStatusSummary
    advocate_performance: list[AdvocatePerformance]