from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # Partner, Advocate, Clerk, Accounts
    created_at = Column(DateTime, default=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    client_type = Column(String(50), default="Individual", nullable=False)  # Individual, Company, Institution
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50))
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    matters = relationship("Matter", back_populates="client")

class Matter(Base):
    __tablename__ = "matters"
    id = Column(Integer, primary_key=True, index=True)
    matter_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    practice_area = Column(String(100), nullable=False)  # Litigation, Conveyancing, Commercial
    status = Column(String(50), default="Open")
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    assigned_advocate_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="matters")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False) 
    status = Column(String(50), default="Pending") 
    priority = Column(String(50), default="Normal") 
    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to_id])

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(100), unique=True, index=True, nullable=False)
    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="Unpaid")  
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="invoices")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by_id])

class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)  
    hourly_rate = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)  
    is_billable = Column(Boolean, default=True)
    is_billed = Column(Boolean, default=False)
    date_performed = Column(DateTime, default=datetime.utcnow)

    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="time_entries")
    user = relationship("User", foreign_keys=[user_id])
    invoice = relationship("Invoice", backref="time_entries")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)  
    location = Column(String(255), nullable=True)     
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="events")
    creator = relationship("User", foreign_keys=[created_by_id])
    assignee = relationship("User", foreign_keys=[assigned_to_id])

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)        
    entity_type = Column(String(50), nullable=False)   # Matter, Document, Invoice, Client,...
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)              
    ip_address = Column(String(50), nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])

class Counterparty(Base):
    __tablename__ = "counterparties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    role = Column(String(100), nullable=False)  # Defendant, Co-defendant, Adverse Party, Parent Company
    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="counterparties")

class TrustAccount(Base):
    __tablename__ = "trust_accounts"

    id = Column(Integer, primary_key=True, index=True)
    matter_id = Column(Integer, ForeignKey("matters.id"), unique=True, nullable=False)
    balance = Column(Numeric(12, 2), default=0.00, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="trust_account")

class TrustTransaction(Base):
    __tablename__ = "trust_transactions"

    id = Column(Integer, primary_key=True, index=True)
    trust_account_id = Column(Integer, ForeignKey("trust_accounts.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # Desposit, Disbursement, Inoice Payment
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trust_account = relationship("TrustAccount", backref="transactions")
    invoice = relationship("Invoice", backref="trust_transactions")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)  # Court Fees, Process Server, Registry Search, Travel, Copying
    description = Column(Text, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    is_reimbursable = Column(Boolean, default=True)  # True = Billable to client (Disbursement)
    is_billed = Column(Boolean, default=False)
    expense_date = Column(DateTime, default=datetime.utcnow)

    matter_id = Column(Integer, ForeignKey("matters.id"), nullable=False)
    paid_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    matter = relationship("Matter", backref="expenses")
    paid_by = relationship("User", foreign_keys=[paid_by_id])
    invoice = relationship("Invoice", backref="expenses")