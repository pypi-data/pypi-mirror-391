"""SQLAlchemy database models for BugBountyCrawler."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from .connection import Base


class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    preferences = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    password_changed_at = Column(DateTime)
    
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    two_factor_secret = Column(String(255))
    recovery_codes = Column(JSON)
    
    total_scans = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)
    last_activity = Column(DateTime)
    
    tags = Column(JSON)
    notes = Column(Text)
    raw_data = Column(JSON)
    
    # Relationships
    scans = relationship("Scan", back_populates="creator")
    findings = relationship("Finding", back_populates="creator")


class Program(Base):
    """Program database model."""
    
    __tablename__ = "programs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    url = Column(String(500))
    
    platform = Column(String(50), nullable=False)
    program_id = Column(String(100))
    program_url = Column(String(500))
    
    scope = Column(JSON)
    
    status = Column(String(20), default="active")
    program_type = Column(String(20), default="public")
    bounty_range = Column(String(100))
    average_bounty = Column(Float)
    
    contact_email = Column(String(255))
    security_team = Column(String(255))
    
    total_findings = Column(Integer, default=0)
    accepted_findings = Column(Integer, default=0)
    total_payout = Column(Float, default=0.0)
    average_response_time = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scan = Column(DateTime)
    
    tags = Column(JSON)
    notes = Column(Text)
    raw_data = Column(JSON)
    
    # Relationships
    scans = relationship("Scan", back_populates="program")
    targets = relationship("Target", back_populates="program")


class Scan(Base):
    """Scan database model."""
    
    __tablename__ = "scans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    program_id = Column(String, ForeignKey("programs.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default="pending")
    scan_type = Column(String(20), default="full")
    
    config = Column(JSON)
    progress = Column(JSON)
    
    target_urls = Column(JSON)
    discovered_urls = Column(JSON)
    excluded_urls = Column(JSON)
    
    findings = Column(JSON)
    screenshots = Column(JSON)
    reports = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    approved_by = Column(String, ForeignKey("users.id"))
    
    tags = Column(JSON)
    notes = Column(Text)
    raw_data = Column(JSON)
    
    # Relationships
    program = relationship("Program", back_populates="scans")
    creator = relationship("User", back_populates="scans", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    scan_targets = relationship("Target", back_populates="scan")
    scan_findings = relationship("Finding", back_populates="scan")


class Target(Base):
    """Target database model."""
    
    __tablename__ = "targets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    program_id = Column(String, ForeignKey("programs.id"), nullable=False)
    scan_id = Column(String, ForeignKey("scans.id"))
    
    target = Column(String(1000), nullable=False, index=True)
    target_type = Column(String(20), nullable=False)
    status = Column(String(20), default="pending")
    
    domain = Column(String(255), index=True)
    ip_address = Column(String(45), index=True)
    port = Column(Integer)
    protocol = Column(String(10), default="https")
    path = Column(String(1000), default="/")
    
    discovered_by = Column(String(100))
    parent_target = Column(String, ForeignKey("targets.id"))
    depth = Column(Integer, default=0)
    
    title = Column(String(500))
    status_code = Column(Integer)
    content_type = Column(String(100))
    content_length = Column(Integer)
    server = Column(String(255))
    technologies = Column(JSON)
    
    ssl_certificate = Column(JSON)
    security_headers = Column(JSON)
    vulnerabilities = Column(JSON)
    
    scan_count = Column(Integer, default=0)
    last_scanned = Column(DateTime)
    response_time = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tags = Column(JSON)
    notes = Column(Text)
    raw_data = Column(JSON)
    
    # Relationships
    program = relationship("Program", back_populates="targets")
    scan = relationship("Scan", back_populates="scan_targets")
    parent = relationship("Target", remote_side=[id])
    target_findings = relationship("Finding", back_populates="target")
    
    # Indexes
    __table_args__ = (
        Index("idx_target_program", "program_id"),
        Index("idx_target_scan", "scan_id"),
        Index("idx_target_domain", "domain"),
        Index("idx_target_ip", "ip_address"),
        Index("idx_target_type", "target_type"),
        Index("idx_target_status", "status"),
    )


class Finding(Base):
    """Finding database model."""
    
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.id"), nullable=False)
    target_id = Column(String, ForeignKey("targets.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default="pending", index=True)
    finding_type = Column(String(50), nullable=False, index=True)
    
    url = Column(String(1000), nullable=False)
    method = Column(String(10), default="GET")
    parameter = Column(String(255))
    payload = Column(Text)
    response_code = Column(Integer)
    
    impact = Column(Text, nullable=False)
    likelihood = Column(String(20), nullable=False)
    risk_score = Column(Float, nullable=False)
    
    proof_of_concept = Column(JSON)
    remediation = Column(JSON)
    
    cvss_vector = Column(String(100))
    cvss_score = Column(Float)
    
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    approved_at = Column(DateTime)
    submitted_at = Column(DateTime)
    
    tags = Column(JSON)
    references = Column(JSON)
    raw_data = Column(JSON)
    
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(String, ForeignKey("users.id"))
    rejection_reason = Column(Text)
    
    # Relationships
    scan = relationship("Scan", back_populates="scan_findings")
    target = relationship("Target", back_populates="target_findings")
    creator = relationship("User", back_populates="findings")
    approver = relationship("User", foreign_keys=[approved_by])
    
    # Indexes
    __table_args__ = (
        Index("idx_finding_scan", "scan_id"),
        Index("idx_finding_target", "target_id"),
        Index("idx_finding_severity", "severity"),
        Index("idx_finding_status", "status"),
        Index("idx_finding_type", "finding_type"),
        Index("idx_finding_discovered", "discovered_at"),
        Index("idx_finding_approved", "approved_at"),
    )


class ScanLog(Base):
    """Scan log database model."""
    
    __tablename__ = "scan_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.id"), nullable=False)
    
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(100))
    function = Column(String(100))
    line = Column(Integer)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    extra_data = Column(JSON)
    
    # Relationships
    scan = relationship("Scan")


class AuditLog(Base):
    """Audit log database model."""
    
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String, nullable=False)
    
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_timestamp", "timestamp"),
    )
