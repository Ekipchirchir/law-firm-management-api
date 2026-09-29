from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Task, Matter, User
from app.schemas import TaskCreate, TaskResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/tasks", tags=["Court Diary & Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Partner", "Advocate", "Clerk"]))
):
    """Schedule a court hearing, deadline, or internal task (Partners, Advocates, Clerks)."""
    matter_result = await db.execute(select(Matter).where(Matter.id == task_data.matter_id))
    if not matter_result.scalars().first():
        raise HTTPException(status_code=404, detail="Matter not found")

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        matter_id=task_data.matter_id,
        assigned_to_id=task_data.assigned_to_id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all scheduled tasks and court diary dates across the firm."""
    result = await db.execute(select(Task).offset(skip).limit(limit))
    tasks = result.scalars().all()
    return tasks

@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update status of a task or court event (e.g., Pending -> Completed)."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = new_status
    await db.commit()
    await db.refresh(task)
    return task