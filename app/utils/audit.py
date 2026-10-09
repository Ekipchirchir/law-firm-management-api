from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog

async def log_activity(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    details: str | None = None,
    user_id: int | None = None,
    request: Request | None = None
):
    ip_address = request.client.host if request and request.client else None
    
    log_entry = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        user_id=user_id,
        ip_address=ip_address
    )
    
    db.add(log_entry)
    await db.commit()