from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, JSON, Float, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="viewer")  # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alerts = relationship("Alert", back_populates="user", foreign_keys="Alert.assigned_to")
    incidents = relationship("Incident", back_populates="user", foreign_keys="Incident.assigned_to")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    source_ip = Column(String(45), index=True)
    dest_ip = Column(String(45), index=True)
    source_port = Column(Integer)
    dest_port = Column(Integer)
    protocol = Column(String(20))
    action = Column(String(100))
    severity = Column(String(20), default="info")  # info, warning, high, critical
    raw_log = Column(Text)
    parsed_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alerts = relationship("Alert", back_populates="log")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="open")  # open, acknowledged, resolved
    source_log_id = Column(Integer, ForeignKey("logs.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    log = relationship("Log", back_populates="alerts")
    user = relationship("User", back_populates="alerts", foreign_keys=[assigned_to])


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="new")  # new, investigating, contained, resolved
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="incidents", foreign_keys=[assigned_to])


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    condition_field = Column(String(50), nullable=False)  # source_ip, dest_port, action, protocol
    operator = Column(String(20), nullable=False)  # equals, contains, greater_than, less_than, regex
    value = Column(String(255), nullable=False)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())