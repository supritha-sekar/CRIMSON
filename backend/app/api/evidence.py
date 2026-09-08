from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib
from datetime import datetime, timezone

from app.database import get_db
from app.models import Evidence, ActivityLog, Case
from app.schemas import EvidenceOut, EvidenceCreate

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("", response_model=List[EvidenceOut])
def get_evidence_items(
    case_id: Optional[int] = None,
    evidence_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Evidence)
    if case_id:
        query = query.filter(Evidence.case_id == case_id)
    if evidence_type and evidence_type != "ALL":
        query = query.filter(Evidence.evidence_type == evidence_type)
    if status and status != "ALL":
        query = query.filter(Evidence.status == status)
    if search:
        query = query.filter(
            (Evidence.title.ilike(f"%{search}%")) |
            (Evidence.evidence_number.ilike(f"%{search}%")) |
            (Evidence.description.ilike(f"%{search}%"))
        )
    return query.order_by(Evidence.created_at.desc()).all()

@router.get("/{evidence_id}", response_model=EvidenceOut)
def get_evidence(evidence_id: int, db: Session = Depends(get_db)):
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return ev

@router.post("", response_model=EvidenceOut, status_code=201)
def create_evidence(ev_in: EvidenceCreate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == ev_in.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Target case not found")

    count = db.query(Evidence).count() + 1
    ev_num = f"EVI-2026-{count:03d}"

    # Auto hash if not provided
    ref_hash = ev_in.reference_hash
    if not ref_hash:
        raw_str = f"{ev_in.title}-{ev_in.description}-{datetime.now(timezone.utc).isoformat()}"
        ref_hash = hashlib.sha256(raw_str.encode()).hexdigest()

    db_ev = Evidence(
        evidence_number=ev_num,
        case_id=ev_in.case_id,
        title=ev_in.title,
        evidence_type=ev_in.evidence_type,
        description=ev_in.description,
        source=ev_in.source or "Analyst Submission",
        collection_date=ev_in.collection_date or datetime.now(timezone.utc),
        status=ev_in.status,
        reference_hash=ref_hash,
        file_path=ev_in.file_path
    )
    db.add(db_ev)
    db.commit()
    db.refresh(db_ev)

    log = ActivityLog(
        action="Evidence Added",
        entity_type="Evidence",
        entity_id=db_ev.id,
        details=f"Added evidence {db_ev.evidence_number} to case {case.case_number}"
    )
    db.add(log)
    db.commit()

    return db_ev
