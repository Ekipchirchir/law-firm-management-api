from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Matter, Client, User
from app.schemas import MatterCreate, MatterResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/matters", tags=["Matter & Case Management"])

@router.post("/", response_model=MatterResponse, status_code=status.HTTP_201_CREATED)
async def create_matter(
    matter_data: MatterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Partner", "Advocate", "Admin"]))
):
    """Open a new legal matter/case (Partners and Advocates only)."""
    # Verify client exists
    client_result = await db.execute(select(Client).where(Client.id == matter_data.client_id))
    if not client_result.scalars().first():
        raise HTTPException(status_code=404, detail="Client not found")

    # Verify unique matter number
    existing_matter = await db.execute(select(Matter).where(Matter.matter_number == matter_data.matter_number))
    if existing_matter.scalars().first():
        raise HTTPException(status_code=400, detail="A matter with this number already exists")

    new_matter = Matter(
        matter_number=matter_data.matter_number,
        title=matter_data.title,
        practice_area=matter_data.practice_area,
        client_id=matter_data.client_id,
        assigned_advocate_id=matter_data.assigned_advocate_id
    )
    db.add(new_matter)
    await db.commit()
    await db.refresh(new_matter)
    return new_matter

@router.get("/", response_model=list[MatterResponse])
async def list_matters(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all matters/cases across the firm (Available to all authenticated staff)."""
    result = await db.execute(select(Matter).offset(skip).limit(limit))
    matters = result.scalars().all()
    return matters

@router.get("/{matter_id}", response_model=MatterResponse)
async def get_matter(
    matter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve detailed information for a specific matter by ID."""
    result = await db.execute(select(Matter).where(Matter.id == matter_id))
    matter = result.scalars().first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter