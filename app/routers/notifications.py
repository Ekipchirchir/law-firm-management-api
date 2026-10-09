from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Notification, Event, User, Matter, Client
from app.schemas import NotificationCreate, NotificationResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications & Alerts"])

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not notification_data.recipient_email and not notification_data.recipient_phone:
        raise HTTPException(status_code=400, detail="Must provide at least an email or phone number")

    notification = Notification(
        recipient_email=notification_data.recipient_email,
        recipient_phone=notification_data.recipient_phone,
        channel=notification_data.channel,
        subject=notification_data.subject,
        message=notification_data.message,
        scheduled_at=notification_data.scheduled_at or datetime.utcnow(),
        user_id=notification_data.user_id,
        client_id=notification_data.client_id,
        matter_id=notification_data.matter_id,
    )

    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification

@router.get("/pending", response_model=list[NotificationResponse])
async def list_pending_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Notification).where(
        Notification.status == "Pending",
        Notification.scheduled_at <= datetime.utcnow()
    ).order_by(Notification.scheduled_at.asc())
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/trigger-court-reminders", status_code=status.HTTP_200_OK)
async def trigger_court_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find events in the next 24 hours
    now = datetime.utcnow()
    tomorrow = now + timedelta(days=1)
    
    stmt = select(Event).where(
        Event.start_time >= now,
        Event.start_time <= tomorrow,
        Event.event_type == "Court Hearing"
    )
    events = (await db.execute(stmt)).scalars().all()

    created_count = 0
    for event in events:
        # Check if notification already generated for event
        msg = f"Reminder: Court Hearing '{event.title}' scheduled for {event.start_time.strftime('%Y-%m-%d %H:%M')} at {event.location or 'Court'}."
        
        existing_stmt = select(Notification).where(
            Notification.matter_id == event.matter_id,
            Notification.message == msg
        )
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()

        if not existing:
            notif = Notification(
                recipient_email=current_user.email,
                channel="EMAIL",
                subject=f"Court Reminder: {event.title}",
                message=msg,
                user_id=event.assigned_to_id or current_user.id,
                matter_id=event.matter_id,
                status="Pending"
            )
            db.add(notif)
            created_count += 1

    await db.commit()
    return {"message": f"Successfully queued {created_count} court hearing reminders."}