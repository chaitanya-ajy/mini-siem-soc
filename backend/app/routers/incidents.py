from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List

from .. import database
from ..models import Incident, User, Log
from ..schemas import IncidentCreate, IncidentResponse, IncidentStatusUpdate

router = APIRouter()


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(incident: IncidentCreate, db: AsyncSession = Depends(database.get_db)):
    db_incident = Incident(
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status="new",
        assigned_to=incident.assigned_to
    )

    db.add(db_incident)
    await db.commit()
    await db.refresh(db_incident)

    return IncidentResponse(
        id=db_incident.id,
        title=db_incident.title,
        description=db_incident.description,
        severity=db_incident.severity,
        status=db_incident.status,
        assigned_to=db_incident.assigned_to,
        created_at=db_incident.created_at,
        resolved_at=db_incident.resolved_at
    )


@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(database.get_db)
):
    query = select(Incident)
    count_query = select(func.count(Incident.id))

    # Apply filters
    if severity:
        query = query.where(Incident.severity == severity)
        count_query = count_query.where(Incident.severity == severity)
    if status:
        query = query.where(Incident.status == status)
        count_query = count_query.where(Incident.status == status)

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply pagination and ordering
    query = query.order_by(Incident.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    incidents = result.scalars().all()

    response_incidents = []
    for inc in incidents:
        username = None
        if inc.assigned_to:
            user_result = await db.execute(select(User).where(User.id == inc.assigned_to))
            user = user_result.scalars().first()
            if user:
                username = user.username

        response_incidents.append(IncidentResponse(
            id=inc.id,
            title=inc.title,
            description=inc.description,
            severity=inc.severity,
            status=inc.status,
            assigned_to=inc.assigned_to,
            created_at=inc.created_at,
            resolved_at=inc.resolved_at,
            username=username
        ))

    return response_incidents


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: int, db: AsyncSession = Depends(database.get_db)):
    query = select(Incident).where(Incident.id == incident_id)
    result = await db.execute(query)
    incident = result.scalars().first()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    # Get assigned user info
    username = None
    if incident.assigned_to:
        user_result = await db.execute(select(User).where(User.id == incident.assigned_to))
        user = user_result.scalars().first()
        if user:
            username = user.username

    return IncidentResponse(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        assigned_to=incident.assigned_to,
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
        username=username
    )


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: int,
    status_update: IncidentStatusUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    query = select(Incident).where(Incident.id == incident_id)
    result = await db.execute(query)
    incident = result.scalars().first()

    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    incident.status = status_update.status
    if status_update.status == "resolved" and not incident.resolved_at:
        incident.resolved_at = datetime.utcnow()
    elif status_update.status != "resolved":
        incident.resolved_at = None

    if status_update.assigned_to is not None:
        incident.assigned_to = status_update.assigned_to

    await db.commit()
    await db.refresh(incident)

    # Get assigned user info
    username = None
    if incident.assigned_to:
        user_result = await db.execute(select(User).where(User.id == incident.assigned_to))
        user = user_result.scalars().first()
        if user:
            username = user.username

    return IncidentResponse(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        assigned_to=incident.assigned_to,
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
        username=username
    )