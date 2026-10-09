from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.database import get_db
from app.models import Event, Matter, User
from app.schemas import EventCreate, EventResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/events", tags=["Calendar & Court Scheduling"])

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    matter = await db.get(Matter, event_data.matter_id)
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    if event_data.end_time <= event_data.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    event = Event(
        title=event_data.title,
        description=event_data.description,
        event_type=event_data.event_type,
        location=event_data.location,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        matter_id=event_data.matter_id,
        created_by_id=current_user.id,
        assigned_to_id=event_data.assigned_to_id or current_user.id
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

@router.get("/matter/{matter_id}", response_model=list[EventResponse])
async def list_events_for_matter(
    matter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Event).where(Event.matter_id == matter_id).order_by(Event.start_time.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/upcoming", response_model=list[EventResponse])
async def list_upcoming_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.utcnow()
    stmt = select(Event).where(Event.start_time >= now).order_by(Event.start_time.asc())
    result = await db.execute(stmt)
    return result.scalars().all()