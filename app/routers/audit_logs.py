from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import AuditLog, User
from app.schemas import AuditLogResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("/", response_model=list[AuditLogResponse])
async def list_audit_logs(
    entity_type: str | None = Query(None, description="Filter by entity type (e.g., Matter, Invoice)"),
    user_id: int | None = Query(None, description="Filter by performing user ID"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["Partner", "Admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    stmt = select(AuditLog).order_by(AuditLog.created_at.desc())

    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()