import re
import json
from datetime import datetime
from typing import Dict, Any


def parse_log(raw_log: str) -> Dict[str, Any]:
    """Parse a log entry into structured fields. Supports JSON, Syslog, and key-value formats."""
    raw_log = raw_log.strip()

    # Try JSON format first
    try:
        parsed = json.loads(raw_log)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Common patterns
    patterns = [
        # Syslog: "Jan 15 10:15:30 server sshd[1234]: Failed password for invalid user admin from 192.168.1.100 port 22 ssh2"
        r'^(?P<timestamp>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(?P<source_ip>\S+)\s+(?P<protocol>\S+):.*',
        # Key-value: "source_ip=1.2.3.4 dest_ip=5.6.7.8 action=denied severity=high"
        r'(?P<key>\w+)=\s*(?P<value>[^\s]+)',
        # Generic: "2026-09-09 10:15:30 INFO source_ip=1.2.3.4 dest_ip=5.6.7.8 action=denied"
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<severity>\w+)\s+(?P<message>.*)$',
    ]

    for pattern in patterns:
        match = re.search(pattern, raw_log)
        if match:
            data = match.groupdict()
            if data.get('key') and data.get('value'):
                # Parse all key-value pairs
                kv = {}
                for kv_match in re.finditer(r'(\w+)=\s*([^\s]+)', raw_log):
                    kv[kv_match.group(1)] = kv_match.group(2)
                return kv
            if data.get('timestamp') and data.get('severity') and data.get('message'):
                kv = {}
                for kv_match in re.finditer(r'(\w+)=\s*([^\s]+)', data['message']):
                    kv[kv_match.group(1)] = kv_match.group(2)
                return {**data, **kv}
            return data

    # Fallback: generic key-value parsing
    kv = {}
    for kv_match in re.finditer(r'(\w+)=\s*([^\s]+)', raw_log):
        kv[kv_match.group(1)] = kv_match.group(2)
    return kv


def normalize_severity(severity: str) -> str:
    """Normalize severity levels."""
    severity = severity.lower().strip()
    if severity in ['info', 'information', 'normal']:
        return 'info'
    if severity in ['warning', 'warn']:
        return 'warning'
    if severity in ['high', 'high_severity']:
        return 'high'
    if severity in ['critical', 'crit', 'error']:
        return 'critical'
    return 'info'


def extract_network_fields(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Extract network-related fields from parsed log."""
    normalized = {}
    for key, value in parsed.items():
        if key in ['source_ip', 'src_ip', 'src', 'ip']:
            normalized['source_ip'] = str(value)
        elif key in ['dest_ip', 'dst_ip', 'dst', 'destination']:
            normalized['dest_ip'] = str(value)
        elif key in ['source_port', 'src_port', 'sport']:
            try:
                normalized['source_port'] = int(value)
            except ValueError:
                pass
        elif key in ['dest_port', 'dst_port', 'dport', 'destination_port']:
            try:
                normalized['dest_port'] = int(value)
            except ValueError:
                pass
        elif key in ['protocol', 'proto']:
            normalized['protocol'] = str(value)
        elif key in ['action', 'result', 'status']:
            normalized['action'] = str(value)
        elif key in ['severity', 'level', 'log_level']:
            normalized['severity'] = normalize_severity(str(value))
        else:
            normalized[key] = str(value)
    return normalized


def build_log_record(raw_log: str, timestamp: datetime = None) -> Dict[str, Any]:
    """Build a complete log record from raw log text."""
    parsed = parse_log(raw_log)
    normalized = extract_network_fields(parsed)

    record = {
        'timestamp': timestamp or datetime.utcnow(),
        'source_ip': normalized.get('source_ip'),
        'dest_ip': normalized.get('dest_ip'),
        'source_port': normalized.get('source_port'),
        'dest_port': normalized.get('dest_port'),
        'protocol': normalized.get('protocol'),
        'action': normalized.get('action'),
        'severity': normalized.get('severity', 'info'),
        'raw_log': raw_log,
        'parsed_data': parsed
    }

    return record