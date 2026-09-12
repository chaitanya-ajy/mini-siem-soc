from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, EmailStr


# ============== User Schemas ==============
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=120)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    role: Optional[str] = "viewer"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None
    role: Optional[str] = None


# ============== Log Schemas ==============
class LogBase(BaseModel):
    timestamp: Optional[datetime] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    source_port: Optional[int] = None
    dest_port: Optional[int] = None
    protocol: Optional[str] = None
    action: Optional[str] = None
    severity: str = "info"
    raw_log: str


class LogCreate(LogBase):
    pass


class LogResponse(LogBase):
    id: int
    parsed_data: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    logs: List[LogResponse]
    total: int
    page: int
    per_page: int


# ============== Alert Schemas ==============
class AlertBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    severity: str = Field(default="medium")  # low, medium, high, critical
    source_log_id: Optional[int] = None
    assigned_to: Optional[int] = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    status: str  # open, acknowledged, resolved
    created_at: datetime
    resolved_at: Optional[datetime] = None
    username: Optional[str] = None
    log: Optional[dict] = None

    class Config:
        from_attributes = True


class AlertStatusUpdate(BaseModel):
    status: str  # open, acknowledged, resolved
    assigned_to: Optional[int] = None


class AlertSummaryResponse(BaseModel):
    total: int
    open: int
    acknowledged: int
    resolved: int


# ============== Incident Schemas ==============
class IncidentBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    severity: str = Field(default="medium")  # low, medium, high, critical
    assigned_to: Optional[int] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentResponse(IncidentBase):
    id: int
    status: str  # new, investigating, contained, resolved
    username: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: str  # new, investigating, contained, resolved
    assigned_to: Optional[int] = None


# ============== Threat Detection Schemas ==============
class AlertRuleBase(BaseModel):
    name: str = Field(..., max_length=255)
    condition_field: str = Field(..., max_length=50)
    operator: str = Field(..., max_length=20)  # equals, contains, greater_than, less_than, regex
    value: str = Field(..., max_length=255)
    severity: str = Field(default="medium")
    enabled: bool = True


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleResponse(AlertRuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ThreatDetectionResult(BaseModel):
    matched: bool
    rule_name: str
    alert_severity: str
    alert_title: str
    alert_description: str


# ============== Dashboard Schemas ==============
class DashboardSummaryResponse(BaseModel):
    total_logs: int
    total_alerts: int
    open_alerts: int
    critical_alerts: int
    total_incidents: int
    active_incidents: int
    threats_detected: int
    logs_by_severity: dict
    alerts_by_severity: dict


class DashboardLogsTrendResponse(BaseModel):
    date: str
    count: int


class DashboardAlertTrendResponse(BaseModel):
    date: str
    count: int


class DashboardTopIPResponse(BaseModel):
    source_ip: str
    count: int


class HealthResponse(BaseModel):
    status: str
    timestamp: str