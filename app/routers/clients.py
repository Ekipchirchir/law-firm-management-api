from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Client, User
from app.schemas import ClientCreate, ClientResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/clients", tags=["Client Management"])

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Partner", "Advocate", "Clerk"]))
):
    """Register a new client (Partners, Advocates, and Clerks only)."""
    # Optional: check if client email already exists if provided
    if client_data.email:
        existing = await db.execute(select(Client).where(Client.email == client_data.email))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="A client with this email already exists")

    new_client = Client(
        name=client_data.name,
        email=client_data.email,
        phone=client_data.phone,
        address=client_data.address,
        client_type=client_data.client_type
    )
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    return new_client

@router.get("/", response_model=list[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all registered clients (Available to any authenticated staff member)."""
    result = await db.execute(select(Client).offset(skip).limit(limit))
    clients = result.scalars().all()
    return clients

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve details for a specific client by ID."""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client