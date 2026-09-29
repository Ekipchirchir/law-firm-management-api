from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Numeric
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
    client_type = Column(String(50), nullable=False)  # Individual, Company, Institution
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