from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserOut"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "Analyst"
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: str
    password: str

# Case Schemas
class CaseBase(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    status: str = "OPEN"      # OPEN, INVESTIGATING, PENDING, RESOLVED, ARCHIVED
    assigned_analyst_id: Optional[int] = None
    tags: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_analyst_id: Optional[int] = None
    risk_score: Optional[int] = None
    tags: Optional[str] = None

class CaseOut(CaseBase):
    id: int
    case_number: str
    risk_score: int
    created_at: datetime
    updated_at: datetime
    assigned_analyst: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)

class CaseLinkOut(BaseModel):
    """Lightweight case schema used in related-cases lists."""
    id: int
    case_number: str
    title: str
    category: str
    priority: str
    status: str
    risk_score: int
    relation_type: str  # e.g. 'shares_suspect', 'continuation_of', etc.
    relationship_id: int

    model_config = ConfigDict(from_attributes=True)

# Case Event Schema
class CaseEventCreate(BaseModel):
    case_id: int
    title: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    event_type: str = "milestone"

class CaseEventOut(BaseModel):
    id: int
    case_id: int
    title: str
    description: Optional[str]
    event_date: datetime
    event_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    entity_type: str  # Person, Organization, Location, Event, Object, Digital Entity
    description: Optional[str] = None
    identifiers_json: Optional[str] = None
    notes: Optional[str] = None
    risk_level: str = "MEDIUM"
    risk_score: int = 45

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    entity_type: Optional[str] = None
    description: Optional[str] = None
    identifiers_json: Optional[str] = None
    notes: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None

class SubjectOut(SubjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Evidence Schemas
class EvidenceBase(BaseModel):
    case_id: int
    title: str
    evidence_type: str  # Document, Text, Image/Reference, URL, Record, Other
    description: Optional[str] = None
    source: Optional[str] = None
    collection_date: Optional[datetime] = None
    status: str = "VERIFIED"
    reference_hash: Optional[str] = None
    file_path: Optional[str] = None

class EvidenceCreate(EvidenceBase):
    pass

class EvidenceOut(EvidenceBase):
    id: int
    evidence_number: str
    created_by_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# AI Analysis Request & Response
class AnalysisRequest(BaseModel):
    case_id: Optional[int] = None
    query_text: str
    context_text: Optional[str] = None
    subject_id: Optional[int] = None

class AnalysisOut(BaseModel):
    id: int
    case_id: Optional[int]
    query_text: str
    context_text: Optional[str]
    subject_id: Optional[int]
    summary: str
    key_findings: List[str]
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    risk_indicators: List[Dict[str, Any]]
    confidence_score: float
    recommendations: List[str]
    next_steps: List[str]
    is_demo: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Risk Assessment Schemas
class RiskFactor(BaseModel):
    category: str
    factor: str
    impact: int
    description: str

class RiskAssessmentResult(BaseModel):
    score: int
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    factors: List[RiskFactor]
    summary: str
    disclaimer: str = "This score is generated for analytical demonstration purposes."

# Relationship Schemas
class RelationshipCreate(BaseModel):
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    relation_type: str
    confidence: float = 0.90
    notes: Optional[str] = None

class RelationshipOut(RelationshipCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Graph View Schemas
class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # Person, Organization, Location, Event, Object, Digital Entity, Case, Evidence
    risk_level: Optional[str] = "LOW"
    details: Optional[Dict[str, Any]] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    confidence: float = 0.9

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# Report Schemas
class ReportCreate(BaseModel):
    title: str
    report_type: str  # Case Summary, Investigation Report, Intelligence Analysis, Evidence Report, Risk Assessment
    case_id: Optional[int] = None
    format: str = "JSON"

class ReportOut(BaseModel):
    id: int
    report_number: str
    title: str
    report_type: str
    case_id: Optional[int]
    content: Dict[str, Any]
    author_id: Optional[int]
    format: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Activity Log Schema
class ActivityLogOut(BaseModel):
    id: int
    user_id: Optional[int]
    user_name: str
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    details: Optional[str]
    ip_address: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Notification Schema
class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int]
    title: str
    message: str
    notification_type: str
    is_read: bool
    link: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Settings Schema
class SettingUpdate(BaseModel):
    key: str
    value: str
