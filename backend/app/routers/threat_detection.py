from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any

from .. import database
from ..models import AlertRule
from ..schemas import AlertRuleCreate, AlertRuleResponse, ThreatDetectionResult
from ..services.threat_detector import analyze_log, detect_threats_for_log

router = APIRouter()


@router.get("/rules", response_model=List[AlertRuleResponse])
async def get_detection_rules(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(AlertRule).order_by(AlertRule.created_at.desc()))
    rules = result.scalars().all()
    return rules


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_detection_rule(rule: AlertRuleCreate, db: AsyncSession = Depends(database.get_db)):
    db_rule = AlertRule(**rule.model_dump())
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.get("/sample")
async def get_sample_threats():
    """Returns sample threat detection for demonstration."""
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
            'raw_log': 'Port scan detected from 203.0.113.50 - attempting ports 22, 80, 443, 3306'
        },
        {
            'source_ip': '198.51.100.10',
            'dest_ip': '10.0.0.5',
            'action': 'injection',
            'severity': 'critical',
            'raw_log': "SELECT * FROM users WHERE username='admin' OR 1=1-- DROP TABLE users;"
        }
    ]

    results = []
    for log_data in sample_logs:
        threats = analyze_log(log_data, None)
        for threat in threats:
            results.append({
                "matched": threat["matched"],
                "rule_name": threat["rule_name"],
                "alert_severity": threat["alert_severity"],
                "alert_title": threat["alert_title"],
                "alert_description": threat["alert_description"]
            })

    return {"sample_threats": results}