from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.database import get_db
from app.models import TimeEntry, Matter, User, Invoice
from app.schemas import TimeEntryCreate, TimeEntryResponse, InvoiceFromTimeEntriesCreate, InvoiceResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/time-entries", tags=["Time Tracking"])

@router.post("/", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
async def log_time(
    entry_data: TimeEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    matter = await db.get(Matter, entry_data.matter_id)
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    user_rate = getattr(current_user, "hourly_rate", 0.0) or 0.0
    total = entry_data.hours * float(user_rate) if entry_data.is_billable else 0.0

    new_entry = TimeEntry(
        description=entry_data.description,
        hours=entry_data.hours,
        hourly_rate=user_rate,
        total_amount=total,
        is_billable=entry_data.is_billable,
        date_performed=entry_data.date_performed or datetime.utcnow(),
        matter_id=entry_data.matter_id,
        user_id=current_user.id
    )
    
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry

@router.get("/matter/{matter_id}/unbilled", response_model=list[TimeEntryResponse])
async def get_unbilled_entries(
    matter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(TimeEntry).where(
        TimeEntry.matter_id == matter_id,
        TimeEntry.is_billable == True,
        TimeEntry.is_billed == False
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/generate-invoice", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def generate_invoice_from_time(
    data: InvoiceFromTimeEntriesCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(TimeEntry).where(
        TimeEntry.id.in_(data.time_entry_ids),
        TimeEntry.matter_id == data.matter_id,
        TimeEntry.is_billed == False
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()

    if not entries:
        raise HTTPException(status_code=400, detail="No valid unbilled time entries selected")

    total_amount = sum(float(e.total_amount) for e in entries)

    invoice = Invoice(
        invoice_number=data.invoice_number,
        matter_id=data.matter_id,
        amount=total_amount,
        due_date=data.due_date,
        status="Unpaid"
    )
    db.add(invoice)
    await db.flush()

    for entry in entries:
        entry.is_billed = True
        entry.invoice_id = invoice.id

    await db.commit()
    await db.refresh(invoice)
    return invoice