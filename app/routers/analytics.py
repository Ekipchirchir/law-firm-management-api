from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.database import get_db
from app.models import User, Matter, Invoice, TimeEntry, TrustAccount
from app.schemas import (
    DashboardAnalyticsResponse,
    FinancialSummary,
    MatterStatusSummary,
    AdvocatePerformance,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])

@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
async def get_dashboard_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Restrict high-level metrics to Partner, Accounts, or Admin roles
    if current_user.role not in ["Partner", "Accounts", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Financial Metrics
    inv_stmt = select(
        func.coalesce(func.sum(Invoice.amount), 0).label("total_invoiced"),
        func.coalesce(func.sum(Invoice.amount).filter(Invoice.status == "Paid"), 0).label("total_paid"),
        func.coalesce(func.sum(Invoice.amount).filter(Invoice.status == "Unpaid"), 0).label("total_unpaid")
    )
    inv_res = (await db.execute(inv_stmt)).first()

    trust_stmt = select(func.coalesce(func.sum(TrustAccount.balance), 0))
    total_trust = (await db.execute(trust_stmt)).scalar() or 0.0

    financials = FinancialSummary(
        total_invoiced=float(inv_res.total_invoiced),
        total_paid=float(inv_res.total_paid),
        total_unpaid=float(inv_res.total_unpaid),
        total_trust_balances=float(total_trust)
    )

    # Matter Status & Practice Area Breakdown
    total_matters = (await db.execute(select(func.count(Matter.id)))).scalar() or 0
    open_matters = (await db.execute(select(func.count(Matter.id)).where(Matter.status == "Open"))).scalar() or 0
    closed_matters = (await db.execute(select(func.count(Matter.id)).where(Matter.status == "Closed"))).scalar() or 0

    pa_stmt = select(Matter.practice_area, func.count(Matter.id)).group_by(Matter.practice_area)
    pa_res = (await db.execute(pa_stmt)).all()
    by_practice_area = {row[0]: row[1] for row in pa_res}

    matter_stats = MatterStatusSummary(
        total_matters=total_matters,
        open_matters=open_matters,
        closed_matters=closed_matters,
        by_practice_area=by_practice_area
    )

    # Advocate Performance Metrics
    adv_stmt = select(
        User.id,
        User.full_name,
        func.coalesce(func.sum(TimeEntry.hours), 0).label("hours"),
        func.coalesce(func.sum(TimeEntry.total_amount), 0).label("billables")
    ).outerjoin(TimeEntry, TimeEntry.user_id == User.id)\
     .where(User.role.in_(["Advocate", "Partner"]))\
     .group_by(User.id, User.full_name)

    adv_res = (await db.execute(adv_stmt)).all()
    advocate_performance = [
        AdvocatePerformance(
            advocate_id=row.id,
            full_name=row.full_name,
            total_hours_logged=float(row.hours),
            total_billable_amount=float(row.billables)
        )
        for row in adv_res
    ]

    return DashboardAnalyticsResponse(
        financials=financials,
        matter_stats=matter_stats,
        advocate_performance=advocate_performance
    )