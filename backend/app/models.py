from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="Analyst", nullable=False)  # Administrator, Analyst, Viewer
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    assigned_cases = relationship("Case", back_populates="assigned_analyst")
    created_evidence = relationship("Evidence", back_populates="created_by")
    created_reports = relationship("Report", back_populates="author")

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # Cybercrime, Financial Fraud, Counter-Intelligence, Narcotics, Organized Crime, General
    priority = Column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(20), default="OPEN", nullable=False)  # OPEN, INVESTIGATING, PENDING, RESOLVED, ARCHIVED
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_score = Column(Integer, default=30)
    tags = Column(Text, nullable=True)  # JSON or comma-separated string
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    assigned_analyst = relationship("User", back_populates="assigned_cases")
    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    events = relationship("CaseEvent", back_populates="case", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")

class CaseEvent(Base):
    __tablename__ = "case_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, default=utc_now)
    event_type = Column(String(50), default="milestone")
    created_at = Column(DateTime, default=utc_now)

    case = relationship("Case", back_populates="events")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # Person, Organization, Location, Event, Object, Digital Entity
    description = Column(Text, nullable=True)
    identifiers_json = Column(Text, nullable=True)  # JSON array or dict string (alias, passport, IP, crypto wallet, etc.)
    notes = Column(Text, nullable=True)
    risk_level = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Integer, default=45)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    evidence_number = Column(String(50), unique=True, index=True, nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    title = Column(String(255), nullable=False)
    evidence_type = Column(String(50), nullable=False)  # Document, Text, Image/Reference, URL, Record, Other
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    collection_date = Column(DateTime, default=utc_now)
    status = Column(String(50), default="VERIFIED")  # VERIFIED, UNVERIFIED, DISPUTED, ARCHIVED
    reference_hash = Column(String(128), nullable=True)
    file_path = Column(String(500), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    case = relationship("Case", back_populates="evidence_items")
    created_by = relationship("User", back_populates="created_evidence")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    context_text = Column(Text, nullable=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    summary = Column(Text, nullable=False)
    key_findings_json = Column(Text, nullable=True)
    entities_json = Column(Text, nullable=True)
    relationships_json = Column(Text, nullable=True)
    risk_indicators_json = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.88)
    recommendations_json = Column(Text, nullable=True)
    next_steps_json = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    case = relationship("Case", back_populates="analyses")
    subject = relationship("Subject")

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False)  # Subject, Case, Evidence
    source_id = Column(Integer, nullable=False)
    target_type = Column(String(50), nullable=False)  # Subject, Case, Evidence
    target_id = Column(Integer, nullable=False)
    relation_type = Column(String(100), nullable=False)  # works_for, associated_with, owns, located_at, references, member_of, transaction_with
    confidence = Column(Float, default=0.90)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # Case Summary, Investigation Report, Intelligence Analysis, Evidence Report, Risk Assessment
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    content_json = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    format = Column(String(20), default="JSON")  # JSON, PDF, HTML
    created_at = Column(DateTime, default=utc_now)

    case = relationship("Case", back_populates="reports")
    author = relationship("User", back_populates="created_reports")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(255), default="System")
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    created_at = Column(DateTime, default=utc_now)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="INFO")  # INFO, WARNING, CRITICAL, SUCCESS
    is_read = Column(Boolean, default=False)
    link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
