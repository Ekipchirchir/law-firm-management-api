from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.database import get_db
from app.models import Client, Matter, Counterparty, User
from app.schemas import (
    CounterpartyCreate,
    CounterpartyResponse,
    ConflictCheckRequest,
    ConflictCheckResponse,
    ConflictMatch,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/conflicts", tags=["Conflict Check"])

@router.post("/counterparties", response_model=CounterpartyResponse, status_code=status.HTTP_201_CREATED)
async def add_counterparty(
    party_data: CounterpartyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    party = Counterparty(
        name=party_data.name,
        role=party_data.role,
        matter_id=party_data.matter_id
    )
    db.add(party)
    await db.commit()
    await db.refresh(party)
    return party

@router.post("/check", response_model=ConflictCheckResponse)
async def perform_conflict_check(
    request: ConflictCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = f"%{request.search_query.strip()}%"
    matches: list[ConflictMatch] = []

    # Search Clients table
    client_stmt = select(Client).where(
        or_(
            Client.name.ilike(query),
            Client.email.ilike(query)
        )
    )
    client_results = (await db.execute(client_stmt)).scalars().all()
    for c in client_results:
        matches.append(ConflictMatch(
            match_type="Existing Client",
            entity_id=c.id,
            matched_text=c.name,
            details=f"Client registered as {c.client_type} ({c.email or 'No email'})"
        ))

    # Search Counterparties table
    cp_stmt = select(Counterparty).where(Counterparty.name.ilike(query))
    cp_results = (await db.execute(cp_stmt)).scalars().all()
    for cp in cp_results:
        matches.append(ConflictMatch(
            match_type="Adverse Counterparty",
            entity_id=cp.id,
            matched_text=cp.name,
            matter_id=cp.matter_id,
            details=f"Listed as '{cp.role}' in Matter ID #{cp.matter_id}"
        ))

    # Search Matters title
    matter_stmt = select(Matter).where(Matter.title.ilike(query))
    matter_results = (await db.execute(matter_stmt)).scalars().all()
    for m in matter_results:
        matches.append(ConflictMatch(
            match_type="Matter Title",
            entity_id=m.id,
            matched_text=m.title,
            matter_id=m.id,
            details=f"Matter '{m.matter_number}' - Practice Area: {m.practice_area}"
        ))

    return ConflictCheckResponse(
        search_query=request.search_query,
        has_potential_conflict=len(matches) > 0,
        total_matches=len(matches),
        matches=matches
    )