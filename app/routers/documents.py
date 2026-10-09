import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Document, Matter, User
from app.schemas import DocumentResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    matter_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if matter exists
    matter = await db.get(Matter, matter_id)
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    # Save file with unique filename to prevent collisions
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    document = Document(
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        matter_id=matter_id,
        uploaded_by_id=current_user.id,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


@router.get("/matter/{matter_id}", response_model=list[DocumentResponse])
async def list_documents_for_matter(
    matter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Document).where(Document.matter_id == matter_id))
    return result.scalars().all()


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await db.get(Document, document_id)
    if not document or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type=document.file_type or "application/octet-stream",
    )