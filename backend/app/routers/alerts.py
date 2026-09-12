from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from .. import database
from ..models import Alert, User, Log
from ..schemas import AlertCreate, AlertResponse, AlertStatusUpdate, AlertSummaryResponse, AlertRuleCreate

router = APIRouter()


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db: AsyncSession = Depends(database.get_db)):
    db_alert = Alert(
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        status="open",
        source_log_id=alert.source_log_id,
        assigned_to=alert.assigned_to
    )

    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)

    return AlertResponse(
        id=db_alert.id,
        title=db_alert.title,
        description=db_alert.description,
        severity=db_alert.severity,
        status=db_alert.status,
        source_log_id=db_alert.source_log_id,
        assigned_to=db_alert.assigned_to,
        created_at=db_alert.created_at,
        resolved_at=db_alert.resolved_at
    )


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    source_ip: Optional[str] = None,
    db: AsyncSession = Depends(database.get_db)
):
    query = select(Alert)
    count_query = select(func.count(Alert.id))

    # Apply filters
    if severity:
        query = query.where(Alert.severity == severity)
        count_query = count_query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
        count_query = count_query.where(Alert.status == status)
    if source_ip:
        # Filter by source log's source_ip
        query = query.join(Log).where(Log.source_ip == source_ip)
        count_query = count_query.join(Log).where(Log.source_ip == source_ip)

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply pagination and ordering
    query = query.order_by(Alert.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    alerts = result.scalars().all()

    response_alerts = []
    for a in alerts:
        username = None
        if a.assigned_to:
            user_result = await db.execute(select(User).where(User.id == a.assigned_to))
            user = user_result.scalars().first()
            if user:
                username = user.username

        response_alerts.append(AlertResponse(
            id=a.id,
            title=a.title,
            description=a.description,
            severity=a.severity,
            status=a.status,
            source_log_id=a.source_log_id,
            assigned_to=a.assigned_to,
            created_at=a.created_at,
            resolved_at=a.resolved_at,
            username=username
        ))

    return response_alerts


@router.get("/summary", response_model=AlertSummaryResponse)
async def get_alert_summary(
    severity: Optional[str] = None,
    db: AsyncSession = Depends(database.get_db)
):
    # Count by status
    open_count_query = select(func.count(Alert.id)).where(Alert.status == "open")
    acknowledged_count_query = select(func.count(Alert.id)).where(Alert.status == "acknowledged")
    resolved_count_query = select(func.count(Alert.id)).where(Alert.status == "resolved")

    all_count_query = select(func.count(Alert.id))

    if severity:
        open_count_query = open_count_query.where(Alert.severity == severity)
        acknowledged_count_query = acknowledged_count_query.where(Alert.severity == severity)
        resolved_count_query = resolved_count_query.where(Alert.severity == severity)
        all_count_query = all_count_query.where(Alert.severity == severity)

    open_result = await db.execute(open_count_query)
    acknowledged_result = await db.execute(acknowledged_count_query)
    resolved_result = await db.execute(resolved_count_query)
    total_result = await db.execute(all_count_query)

    return AlertSummaryResponse(
        total=total_result.scalar(),
        open=open_result.scalar(),
        acknowledged=acknowledged_result.scalar(),
        resolved=resolved_result.scalar()
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: AsyncSession = Depends(database.get_db)):
    query = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(query)
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    # Get assigned user info
    username = None
    if alert.assigned_to:
        user_result = await db.execute(select(User).where(User.id == alert.assigned_to))
        user = user_result.scalars().first()
        if user:
            username = user.username

    return AlertResponse(
        id=alert.id,
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        status=alert.status,
        source_log_id=alert.source_log_id,
        assigned_to=alert.assigned_to,
        created_at=alert.created_at,
        resolved_at=alert.resolved_at,
        username=username
    )


@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: int,
    status_update: AlertStatusUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    query = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(query)
    alert = result.scalars().first()

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.status = status_update.status
    if status_update.status == "resolved" and not alert.resolved_at:
        alert.resolved_at = datetime.utcnow()
    elif status_update.status != "resolved":
        alert.resolved_at = None

    if status_update.assigned_to is not None:
        alert.assigned_to = status_update.assigned_to

    await db.commit()
    await db.refresh(alert)

    # Get assigned user info
    username = None
    if alert.assigned_to:
        user_result = await db.execute(select(User).where(User.id == alert.assigned_to))
        user = user_result.scalars().first()
        if user:
            username = user.username

    return AlertResponse(
        id=alert.id,
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        status=alert.status,
        source_log_id=alert.source_log_id,
        assigned_to=alert.assigned_to,
        created_at=alert.created_at,
        resolved_at=alert.resolved_at,
        username=username
    )