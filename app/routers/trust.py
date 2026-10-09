from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import TrustAccount, TrustTransaction, Matter, Invoice, User
from app.schemas import (
    TrustDepositRequest,
    ApplyTrustToInvoiceRequest,
    TrustAccountResponse,
    TrustTransactionResponse,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/trust", tags=["Trust Accounting"])

@router.post("/deposit", response_model=TrustTransactionResponse, status_code=status.HTTP_201_CREATED)
async def deposit_retainer(
    data: TrustDepositRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than 0")

    matter = await db.get(Matter, data.matter_id)
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    # Fetch or auto-create trust account for matter
    stmt = select(TrustAccount).where(TrustAccount.matter_id == data.matter_id)
    account = (await db.execute(stmt)).scalar_one_or_none()

    if not account:
        account = TrustAccount(matter_id=data.matter_id, balance=0.00)
        db.add(account)
        await db.flush()

    account.balance = float(account.balance) + data.amount

    tx = TrustTransaction(
        trust_account_id=account.id,
        transaction_type="DEPOSIT",
        amount=data.amount,
        description=data.description
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx

@router.get("/matter/{matter_id}", response_model=TrustAccountResponse)
async def get_trust_account(
    matter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(TrustAccount).where(TrustAccount.matter_id == matter_id)
    account = (await db.execute(stmt)).scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="No trust account found for this matter")
    return account

@router.post("/apply-to-invoice", response_model=TrustTransactionResponse)
async def apply_trust_to_invoice(
    data: ApplyTrustToInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invoice = await db.get(Invoice, data.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    stmt = select(TrustAccount).where(TrustAccount.matter_id == invoice.matter_id)
    account = (await db.execute(stmt)).scalar_one_or_none()

    if not account or float(account.balance) < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient trust funds available")

    # Deduct from trust balance and adjust invoice status
    account.balance = float(account.balance) - data.amount
    
    if data.amount >= float(invoice.amount):
        invoice.status = "Paid"
    else:
        invoice.amount = float(invoice.amount) - data.amount

    tx = TrustTransaction(
        trust_account_id=account.id,
        transaction_type="INVOICE_PAYMENT",
        amount=data.amount,
        description=f"Applied trust funds to Invoice #{invoice.invoice_number}",
        invoice_id=invoice.id
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx