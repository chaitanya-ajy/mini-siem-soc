import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import ipaddress


# Threat detection patterns/rules
BRUTE_FORCE_PATTERNS = [
    r'failed password',
    r'authentication failure',
    r'invalid user',
    r'access denied',
    r'login failed',
]

PORT_SCAN_PATTERNS = [
    r'port scan',
    r'probe',
    r'nmap',
]

SQL_INJECTION_PATTERNS = [
    r'\'.+OR\s+1=1',
    r';\s*DROP',
    r'UNION\s+SELECT',
    r'EXEC\s*\(',
    r'--\s*$',
]

SUSPICIOUS_ACTIONS = [
    'denied',
    'blocked',
    'rejected',
    'dropped',
]

# Private/reserved IP ranges for internal traffic
PRIVATE_IP_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('0.0.0.0/8'),
    ipaddress.ip_network('224.0.0.0/4'),
]


def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private/internal."""
    if not ip_str:
        return True
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in PRIVATE_IP_RANGES:
            if ip in network:
                return True
        return False
    except ValueError:
        return True


class ThreatDetector:
    def __init__(self, db: AsyncSession, log_data: Dict[str, Any]):
        self.db = db
        self.log = log_data
        self.original_log = log_data.get('raw_log', '').lower()
        self.source_ip = log_data.get('source_ip', '')
        self.dest_ip = log_data.get('dest_ip', '')
        self.source_port = log_data.get('source_port')
        self.dest_port = log_data.get('dest_port')
        self.protocol = log_data.get('protocol', '')
        self.action = log_data.get('action', '')
        self.severity = log_data.get('severity', 'info')

    def detect_brute_force(self) -> Optional[Dict[str, Any]]:
        """Detect potential brute force attacks."""
        if any(pattern in self.original_log for pattern in BRUTE_FORCE_PATTERNS):
            return {
                'matched': True,
                'rule_name': 'Brute Force Detection',
                'alert_severity': 'high',
                'alert_title': 'Potential Brute Force Attack Detected',
                'alert_description': f'Failed authentication attempts detected from {self.source_ip}. Possible brute force attack.'
            }
        return None

    def detect_port_scan(self) -> Optional[Dict[str, Any]]:
        """Detect potential port scanning activity."""
        if any(pattern in self.original_log for pattern in PORT_SCAN_PATTERNS):
            return {
                'matched': True,
                'rule_name': 'Port Scan Detection',
                'alert_severity': 'high',
                'alert_title': 'Potential Port Scan Detected',
                'alert_description': f'Port scanning activity detected from {self.source_ip}.'
            }

        # Check for multiple connection attempts to different ports
        if self.dest_port and self.action.lower() in ['denied', 'blocked']:
            return {
                'matched': True,
                'rule_name': 'Port Scan Detection',
                'alert_severity': 'medium',
                'alert_title': 'Suspicious Connection Attempt',
                'alert_description': f'Suspicious connection to port {self.dest_port} from {self.source_ip}.'
            }
        return None

    def detect_sql_injection(self) -> Optional[Dict[str, Any]]:
        """Detect potential SQL injection attempts."""
        if any(pattern in self.original_log for pattern in SQL_INJECTION_PATTERNS):
            return {
                'matched': True,
                'rule_name': 'SQL Injection Detection',
                'alert_severity': 'critical',
                'alert_title': 'Potential SQL Injection Attempt',
                'alert_description': f'SQL injection pattern detected in request from {self.source_ip}.'
            }
        return None

    def detect_suspicious_external(self) -> Optional[Dict[str, Any]]:
        """Detect suspicious activity from external IPs (non-private)."""
        if self.source_ip and not is_private_ip(self.source_ip):
            if any(action in self.action.lower() for action in SUSPICIOUS_ACTIONS):
                return {
                    'matched': True,
                    'rule_name': 'External Suspicious Activity',
                    'alert_severity': 'medium',
                    'alert_title': 'External Suspicious Activity',
                    'alert_description': f'Suspicious activity from external IP {self.source_ip}.'
                }
        return None

    def detect_bad_user(self) -> Optional[Dict[str, Any]]:
        """Detect attempts to access with invalid/bot users."""
        if 'invalid user' in self.original_log or 'unknown user' in self.original_log:
            return {
                'matched': True,
                'rule_name': 'Invalid User Access Attempt',
                'alert_severity': 'medium',
                'alert_title': 'Invalid User Access Attempt',
                'alert_description': f'Access attempt with invalid user from {self.source_ip}.'
            }
        return None

    def run_all_detections(self) -> List[Dict[str, Any]]:
        """Run all threat detection methods."""
        detections = []

        for method in [
            self.detect_sql_injection,
            self.detect_brute_force,
            self.detect_port_scan,
            self.detect_bad_user,
            self.detect_suspicious_external,
        ]:
            result = method()
            if result:
                detections.append(result)

        return detections


def analyze_log(log_data: Dict[str, Any], db: AsyncSession) -> List[Dict[str, Any]]:
    """Analyze a single log entry for threats."""
    detector = ThreatDetector(db, log_data)
    return detector.run_all_detections()


def check_rule_trigger(rule_field: str, rule_operator: str, rule_value: str, log_data: Dict[str, Any]) -> bool:
    """Check if a custom rule triggers on the log."""
    log_value = str(log_data.get(rule_field, '')).lower() if rule_field else ''
    rule_val_lower = rule_value.lower()

    if rule_operator == 'equals':
        return log_value == rule_val_lower
    elif rule_operator == 'contains':
        return rule_val_lower in log_value
    elif rule_operator == 'regex':
        try:
            return bool(re.search(rule_value, log_value, re.IGNORECASE))
        except re.error:
            return False
    elif rule_operator == 'greater_than':
        try:
            return float(log_value) > float(rule_val_lower)
        except ValueError:
            return False
    elif rule_operator == 'less_than':
        try:
            return float(log_value) < float(rule_val_lower)
        except ValueError:
            return False
    return False


async def check_custom_rules(db: AsyncSession, log_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check if log matches any custom alert rules from database."""
    from ..models import AlertRule

    query = select(AlertRule).where(AlertRule.enabled == True)
    result = await db.execute(query)
    rules = result.scalars().all()

    alerts = []
    for rule in rules:
        if check_rule_trigger(rule.condition_field, rule.operator, rule.value, log_data):
            alerts.append({
                'matched': True,
                'rule_name': rule.name,
                'alert_severity': rule.severity,
                'alert_title': f'Threat Detected: {rule.name}',
                'alert_description': f'Log matched rule: {rule.name} (Field: {rule.condition_field} {rule.operator} {rule.value})'
            })

    return alerts


async def detect_threats_for_log(log_id: int, db: AsyncSession, log_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Main entry point for threat detection on a log entry."""
    # Run built-in detections
    detections = analyze_log(log_data, db)

    # Run custom rules from database
    custom_alerts = await check_custom_rules(db, log_data)
    detections.extend(custom_alerts)

    return detections