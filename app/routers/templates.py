import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from app.database import get_db
from app.models import DocumentTemplate, Matter, Document, User
from app.schemas import (
    DocumentTemplateCreate,
    DocumentTemplateResponse,
    GenerateDocumentRequest,
    DocumentResponse,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/templates", tags=["Document Templates"])

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=DocumentTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: DocumentTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = DocumentTemplate(
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        content_template=template_data.content_template
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/", response_model=list[DocumentTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(DocumentTemplate))
    return result.scalars().all()


@router.post("/generate", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def generate_document_from_template(
    data: GenerateDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = await db.get(DocumentTemplate, data.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Document template not found")

    # Fetch Matter with loaded Client
    stmt = select(Matter).options(selectinload(Matter.client)).where(Matter.id == data.matter_id)
    matter = (await db.execute(stmt)).scalar_one_or_none()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    # Build context dictionary for merging
    context = {
        "client_name": matter.client.name,
        "client_email": matter.client.email or "N/A",
        "client_address": matter.client.address or "N/A",
        "matter_number": matter.matter_number,
        "matter_title": matter.title,
        "practice_area": matter.practice_area,
        "advocate_name": current_user.full_name,
    }

    # Merge custom user variables if supplied
    if data.custom_variables:
        context.update(data.custom_variables)

    # Simple string formatting substitution engine
    generated_content = template.content_template
    for key, val in context.items():
        generated_content = generated_content.replace(f"{{{{{key}}}}}", str(val))

    # Save output text file to uploads directory
    file_filename = f"{template.name.lower().replace(' ', '_')}_{matter.matter_number}.txt"
    unique_filename = f"{uuid.uuid4()}.txt"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(generated_content)

    file_size = len(generated_content.encode("utf-8"))

    # Register generated file in Documents table
    document = Document(
        filename=file_filename,
        file_path=file_path,
        file_type="text/plain",
        file_size=file_size,
        matter_id=matter.id,
        uploaded_by_id=current_user.id
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document