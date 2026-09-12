from datetime import datetime, timedelta, timezone
from sqlalchemy.future import select
from .database import AsyncSessionLocal
from .models import User, AlertRule, Log, Alert, Incident
from .routers.auth import hash_password

async def seed_default_data():
    async with AsyncSessionLocal() as session:
        # 1. Seed Admin User
        user_res = await session.execute(select(User).where(User.username == "admin"))
        admin_user = user_res.scalars().first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@siem.local",
                password_hash=hash_password("admin123"),
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

        # 2. Seed Default Alert Rules
        rules_res = await session.execute(select(AlertRule))
        existing_rules = rules_res.scalars().all()
        if not existing_rules:
            default_rules = [
                AlertRule(
                    name="SSH Brute Force - Failed Password",
                    condition_field="action",
                    operator="contains",
                    value="failed password",
                    severity="high",
                    enabled=True
                ),
                AlertRule(
                    name="SQL Injection Pattern",
                    condition_field="raw_log",
                    operator="regex",
                    value=r"OR\s+1=1|DROP\s+TABLE|UNION\s+SELECT",
                    severity="critical",
                    enabled=True
                ),
                AlertRule(
                    name="Port Scanning Activity",
                    condition_field="raw_log",
                    operator="contains",
                    value="port scan",
                    severity="high",
                    enabled=True
                ),
                AlertRule(
                    name="External Denied Traffic",
                    condition_field="severity",
                    operator="equals",
                    value="high",
                    severity="medium",
                    enabled=True
                )
            ]
            for rule in default_rules:
                session.add(rule)
            await session.commit()

        # 3. Seed Sample Logs, Alerts & Incidents if logs table has <= 1 entry
        logs_res = await session.execute(select(Log))
        existing_logs = logs_res.scalars().all()
        if len(existing_logs) <= 1:
            now = datetime.now(timezone.utc)
            sample_logs = [
                Log(
                    timestamp=now - timedelta(minutes=5),
                    source_ip="198.51.100.23",
                    dest_ip="10.0.0.12",
                    source_port=51234,
                    dest_port=443,
                    protocol="HTTPS",
                    action="injection",
                    severity="critical",
                    raw_log="SQL Injection detected: SELECT * FROM users WHERE '1'='1'--",
                    parsed_data={"pattern": "SQLi", "payload": "1=1--"}
                ),
                Log(
                    timestamp=now - timedelta(minutes=15),
                    source_ip="203.0.113.88",
                    dest_ip="10.0.0.5",
                    source_port=43890,
                    dest_port=22,
                    protocol="SSH",
                    action="failed password",
                    severity="high",
                    raw_log="Failed password for invalid user root from 203.0.113.88 port 43890 ssh2",
                    parsed_data={"auth_method": "password", "target_user": "root"}
                ),
                Log(
                    timestamp=now - timedelta(minutes=30),
                    source_ip="192.168.1.55",
                    dest_ip="10.0.0.8",
                    source_port=60123,
                    dest_port=80,
                    protocol="HTTP",
                    action="denied",
                    severity="medium",
                    raw_log="WAF: Blocked potential path traversal attempt /etc/passwd from 192.168.1.55",
                    parsed_data={"rule_id": "WAF-901"}
                ),
                Log(
                    timestamp=now - timedelta(hours=1),
                    source_ip="203.0.113.50",
                    dest_ip="10.0.0.5",
                    source_port=33100,
                    dest_port=8080,
                    protocol="TCP",
                    action="port scan",
                    severity="high",
                    raw_log="SYN scan detected across ports 21-8080 from 203.0.113.50",
                    parsed_data={"scan_type": "SYN"}
                ),
                Log(
                    timestamp=now - timedelta(hours=2),
                    source_ip="192.168.1.10",
                    dest_ip="10.0.0.1",
                    source_port=52000,
                    dest_port=53,
                    protocol="DNS",
                    action="allowed",
                    severity="info",
                    raw_log="DNS Query response success for api.internal.corp",
                    parsed_data={"query": "api.internal.corp"}
                )
            ]
            for l in sample_logs:
                session.add(l)
            await session.commit()

            # Refresh first two logs for alert linkage
            for l in sample_logs:
                await session.refresh(l)

            # Sample Alerts
            sample_alerts = [
                Alert(
                    title="Critical SQL Injection Attempt",
                    description="SQL injection pattern detected on authentication service from IP 198.51.100.23",
                    severity="critical",
                    status="open",
                    source_log_id=sample_logs[0].id,
                    assigned_to=admin_user.id
                ),
                Alert(
                    title="SSH Brute Force Attack",
                    description="Multiple failed authentication attempts detected from 203.0.113.88 against port 22",
                    severity="high",
                    status="open",
                    source_log_id=sample_logs[1].id,
                    assigned_to=admin_user.id
                ),
                Alert(
                    title="Suspicious Reconnaissance / Port Scan",
                    description="Automated port scan identified scanning web application port ranges",
                    severity="high",
                    status="acknowledged",
                    source_log_id=sample_logs[3].id,
                    assigned_to=admin_user.id
                )
            ]
            for a in sample_alerts:
                session.add(a)
            await session.commit()

            # Sample Incidents
            sample_incidents = [
                Incident(
                    title="Active SQL Injection Campaign targeting Auth DB",
                    description="Automated exploit tools targeting SQL endpoints from untrusted subnet 198.51.100.0/24",
                    severity="critical",
                    status="investigating",
                    assigned_to=admin_user.id
                ),
                Incident(
                    title="External SSH Credential Stuffing Attack",
                    description="Distributed brute force against perimeter bastion host",
                    severity="high",
                    status="new",
                    assigned_to=admin_user.id
                )
            ]
            for inc in sample_incidents:
                session.add(inc)
            await session.commit()
