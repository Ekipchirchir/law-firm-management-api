from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.database import get_db
from app.models import Expense, Matter, Invoice, User
from app.schemas import ExpenseCreate, ExpenseResponse, AttachExpensesToInvoiceRequest, InvoiceResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses & Disbursements"])

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    matter = await db.get(Matter, expense_data.matter_id)
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    if expense_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero")

    expense = Expense(
        category=expense_data.category,
        description=expense_data.description,
        amount=expense_data.amount,
        is_reimbursable=expense_data.is_reimbursable,
        expense_date=expense_data.expense_date or datetime.utcnow(),
        matter_id=expense_data.matter_id,
        paid_by_id=current_user.id
    )

    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense

@router.get("/matter/{matter_id}/unbilled", response_model=list[ExpenseResponse])
async def get_unbilled_expenses(
    matter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Expense).where(
        Expense.matter_id == matter_id,
        Expense.is_reimbursable == True,
        Expense.is_billed == False
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/add-to-invoice", response_model=InvoiceResponse)
async def attach_expenses_to_invoice(
    data: AttachExpensesToInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invoice = await db.get(Invoice, data.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    stmt = select(Expense).where(
        Expense.id.in_(data.expense_ids),
        Expense.matter_id == invoice.matter_id,
        Expense.is_billed == False
    )
    expenses = (await db.execute(stmt)).scalars().all()

    if not expenses:
        raise HTTPException(status_code=400, detail="No unbilled expenses found for this matter")

    total_disbursements = sum(float(e.amount) for e in expenses)
    invoice.amount = float(invoice.amount) + total_disbursements

    for exp in expenses:
        exp.is_billed = True
        exp.invoice_id = invoice.id

    await db.commit()
    await db.refresh(invoice)
    return invoice