from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional, List

from .. import database
from ..models import Log, Alert, Incident
from ..schemas import DashboardSummaryResponse, DashboardLogsTrendResponse, DashboardAlertTrendResponse, DashboardTopIPResponse

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(database.get_db)):
    # Total logs
    total_logs_result = await db.execute(select(func.count(Log.id)))
    total_logs = total_logs_result.scalar()

    # Total alerts
    total_alerts_result = await db.execute(select(func.count(Alert.id)))
    total_alerts = total_alerts_result.scalar()

    # Open alerts
    open_alerts_result = await db.execute(select(func.count(Alert.id)).where(Alert.status == "open"))
    open_alerts = open_alerts_result.scalar()

    # Critical alerts
    critical_alerts_result = await db.execute(select(func.count(Alert.id)).where(Alert.severity == "critical"))
    critical_alerts = critical_alerts_result.scalar()

    # Total incidents
    total_incidents_result = await db.execute(select(func.count(Incident.id)))
    total_incidents = total_incidents_result.scalar()

    # Active incidents (new or investigating)
    active_incidents_result = await db.execute(
        select(func.count(Incident.id)).where(Incident.status.in_(["new", "investigating", "contained"]))
    )
    active_incidents = active_incidents_result.scalar() or 0

    # Logs by severity (last 30 days)
    logs_by_severity_result = await db.execute(
        select(Log.severity, func.count(Log.id))
        .group_by(Log.severity)
    )
    logs_by_severity = {}
    for severity, count in logs_by_severity_result.all():
        logs_by_severity[severity] = count

    # Alerts by severity
    alerts_by_severity_result = await db.execute(
        select(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
    )
    alerts_by_severity = {}
    for severity, count in alerts_by_severity_result.all():
        alerts_by_severity[severity] = count

    return DashboardSummaryResponse(
        total_logs=total_logs,
        total_alerts=total_alerts,
        open_alerts=open_alerts,
        critical_alerts=critical_alerts,
        total_incidents=total_incidents,
        active_incidents=active_incidents,
        threats_detected=total_alerts,
        logs_by_severity=logs_by_severity,
        alerts_by_severity=alerts_by_severity
    )


@router.get("/logs/trend", response_model=List[DashboardLogsTrendResponse])
async def get_logs_trend(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(database.get_db)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(Log.timestamp).label("date"),
            func.count(Log.id).label("count")
        )
        .where(Log.timestamp >= start_date)
        .group_by(func.date(Log.timestamp))
        .order_by(func.date(Log.timestamp))
    )

    return [
        DashboardLogsTrendResponse(date=str(date), count=count)
        for date, count in result.all()
    ]


@router.get("/alerts/trend", response_model=List[DashboardAlertTrendResponse])
async def get_alerts_trend(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(database.get_db)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(Alert.created_at).label("date"),
            func.count(Alert.id).label("count")
        )
        .where(Alert.created_at >= start_date)
        .group_by(func.date(Alert.created_at))
        .order_by(func.date(Alert.created_at))
    )

    return [
        DashboardAlertTrendResponse(date=str(date), count=count)
        for date, count in result.all()
    ]


@router.get("/top-ips", response_model=List[DashboardTopIPResponse])
async def get_top_source_ips(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(database.get_db)
):
    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(Log.source_ip, func.count(Log.id).label("count"))
        .where(Log.source_ip.is_not(None))
        .where(Log.timestamp >= start_date)
        .group_by(Log.source_ip)
        .order_by(desc(func.count(Log.id)))
        .limit(limit)
    )

    return [
        DashboardTopIPResponse(source_ip=ip, count=count)
        for ip, count in result.all()
    ]