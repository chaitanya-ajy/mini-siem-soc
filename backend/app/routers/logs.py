from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from .. import database
from ..models import Log, User
from ..schemas import LogCreate, LogResponse, LogListResponse, ThreatDetectionResult
from ..services.log_ingestion import build_log_record, normalize_severity
from ..services.threat_detector import analyze_log, detect_threats_for_log

router = APIRouter()


@router.post("/", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(log: LogCreate, db: AsyncSession = Depends(database.get_db)):
    timestamp = log.timestamp or datetime.utcnow()
    severity = normalize_severity(log.severity or "info")

    log_record = Log(
        timestamp=timestamp,
        source_ip=log.source_ip,
        dest_ip=log.dest_ip,
        source_port=log.source_port,
        dest_port=log.dest_port,
        protocol=log.protocol,
        action=log.action,
        severity=severity,
        raw_log=log.raw_log,
        parsed_data={}
    )

    db.add(log_record)
    await db.commit()
    await db.refresh(log_record)

    # Run threat detection asynchronously (non-blocking)
    log_data = {
        'source_ip': log.source_ip,
        'dest_ip': log.dest_ip,
        'action': log.action,
        'severity': severity,
        'raw_log': log.raw_log,
        'dest_port': log.dest_port,
    }
    threats = analyze_log(log_data, db)

    return LogResponse(
        id=log_record.id,
        timestamp=log_record.timestamp,
        source_ip=log_record.source_ip,
        dest_ip=log_record.dest_ip,
        source_port=log_record.source_port,
        dest_port=log_record.dest_port,
        protocol=log_record.protocol,
        action=log_record.action,
        severity=log_record.severity,
        raw_log=log_record.raw_log,
        parsed_data=log_record.parsed_data,
        created_at=log_record.created_at
    )


@router.get("/", response_model=LogListResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    source_ip: Optional[str] = None,
    dest_ip: Optional[str] = None,
    protocol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(database.get_db)
):
    query = select(Log)
    count_query = select(func.count(Log.id))

    # Apply filters
    if severity:
        query = query.where(Log.severity == severity)
        count_query = count_query.where(Log.severity == severity)
    if source_ip:
        query = query.where(Log.source_ip == source_ip)
        count_query = count_query.where(Log.source_ip == source_ip)
    if dest_ip:
        query = query.where(Log.dest_ip == dest_ip)
        count_query = count_query.where(Log.dest_ip == dest_ip)
    if protocol:
        query = query.where(Log.protocol == protocol)
        count_query = count_query.where(Log.protocol == protocol)
    if start_date:
        query = query.where(Log.timestamp >= start_date)
        count_query = count_query.where(Log.timestamp >= start_date)
    if end_date:
        query = query.where(Log.timestamp <= end_date)
        count_query = count_query.where(Log.timestamp <= end_date)

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply pagination and ordering
    query = query.order_by(Log.timestamp.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    logs = result.scalars().all()

    log_responses = [
        LogResponse(
            id=l.id,
            timestamp=l.timestamp,
            source_ip=l.source_ip,
            dest_ip=l.dest_ip,
            source_port=l.source_port,
            dest_port=l.dest_port,
            protocol=l.protocol,
            action=l.action,
            severity=l.severity,
            raw_log=l.raw_log,
            parsed_data=l.parsed_data,
            created_at=l.created_at
        )
        for l in logs
    ]

    return LogListResponse(
        logs=log_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{log_id}", response_model=LogResponse)
async def get_log(log_id: int, db: AsyncSession = Depends(database.get_db)):
    query = select(Log).where(Log.id == log_id)
    result = await db.execute(query)
    log = result.scalars().first()

    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    return LogResponse(
        id=log.id,
        timestamp=log.timestamp,
        source_ip=log.source_ip,
        dest_ip=log.dest_ip,
        source_port=log.source_port,
        dest_port=log.dest_port,
        protocol=log.protocol,
        action=log.action,
        severity=log.severity,
        raw_log=log.raw_log,
        parsed_data=log.parsed_data,
        created_at=log.created_at
    )


@router.get("/threats/sample", response_model=List[ThreatDetectionResult])
async def sample_threat_detection():
    """Endpoint to demonstrate threat detection."""
    sample_logs = [
        {
            'source_ip': '192.168.1.100',
            'dest_ip': '10.0.0.5',
            'action': 'failed password',
            'severity': 'high',
            'raw_log': 'Failed password for invalid user admin from 192.168.1.100 port 22 ssh2'
        },
        {
            'source_ip': '203.0.113.50',
            'dest_ip': '10.0.0.5',
            'action': 'denied',
            'severity': 'high',
            'raw_log': 'Port scan detected from 203.0.113.50'
        },
        {
            'source_ip': '198.51.100.10',
            'dest_ip': '10.0.0.5',
            'action': 'injection',
            'severity': 'critical',
            'raw_log': "SELECT * FROM users WHERE username='admin' OR 1=1--"
        }
    ]

    results = []
    for log_data in sample_logs:
        threats = analyze_log(log_data, None)
        for threat in threats:
            results.append(ThreatDetectionResult(
                matched=threat['matched'],
                rule_name=threat['rule_name'],
                alert_severity=threat['alert_severity'],
                alert_title=threat['alert_title'],
                alert_description=threat['alert_description']
            ))

    return results