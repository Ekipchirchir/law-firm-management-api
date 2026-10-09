from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Invoice, Matter, User
from app.schemas import InvoiceCreate, InvoiceResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/billing", tags=["Accounting & Billing"])

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Partner", "Accounts"]))
):
    """Generate a new professional fee note/invoice for a matter (Partners and Accounts only)."""
    matter_result = await db.execute(select(Matter).where(Matter.id == invoice_data.matter_id))
    if not matter_result.scalars().first():
        raise HTTPException(status_code=404, detail="Matter not found")

    # Check for duplicate invoice number
    existing_invoice = await db.execute(select(Invoice).where(Invoice.invoice_number == invoice_data.invoice_number))
    if existing_invoice.scalars().first():
        raise HTTPException(status_code=400, detail="An invoice with this number already exists")

    new_invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        matter_id=invoice_data.matter_id,
        amount=invoice_data.amount,
        due_date=invoice_data.due_date
    )
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)
    return new_invoice

@router.get("/invoices", response_model=list[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all invoices and billing records across the firm."""
    result = await db.execute(select(Invoice).offset(skip).limit(limit))
    invoices = result.scalars().all()
    return invoices

@router.patch("/invoices/{invoice_id}/status", response_model=InvoiceResponse)
async def update_invoice_status(
    invoice_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Partner", "Accounts"]))
):
    """Update invoice payment status (e.g., Unpaid -> Paid)."""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.status = new_status
    await db.commit()
    await db.refresh(invoice)
    return invoice