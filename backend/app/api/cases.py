from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import random

from app.database import get_db
from app.models import Case, CaseEvent, ActivityLog, User, Subject, Relationship
from app.schemas import CaseOut, CaseCreate, CaseUpdate, CaseEventOut, CaseEventCreate, SubjectOut, CaseLinkOut

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("", response_model=List[CaseOut])
def get_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Case)
    if status and status != "ALL":
        query = query.filter(Case.status == status)
    if priority and priority != "ALL":
        query = query.filter(Case.priority == priority)
    if category and category != "ALL":
        query = query.filter(Case.category == category)
    if search:
        query = query.filter(
            (Case.title.ilike(f"%{search}%")) | 
            (Case.case_number.ilike(f"%{search}%")) |
            (Case.description.ilike(f"%{search}%"))
        )
    return query.order_by(Case.created_at.desc()).all()

@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("", response_model=CaseOut, status_code=201)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    case_count = db.query(Case).count() + 1
    case_num = f"CAS-2026-{case_count:03d}"
    
    # Calculate baseline risk score based on priority
    priority_scores = {"LOW": 20, "MEDIUM": 45, "HIGH": 70, "CRITICAL": 90}
    risk_score = priority_scores.get(case_in.priority.upper(), 40)

    db_case = Case(
        case_number=case_num,
        title=case_in.title,
        description=case_in.description,
        category=case_in.category,
        priority=case_in.priority,
        status=case_in.status,
        assigned_analyst_id=case_in.assigned_analyst_id,
        risk_score=risk_score,
        tags=case_in.tags
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    # Initial Event
    event = CaseEvent(
        case_id=db_case.id,
        title="Case Created",
        description=f"Case opened with priority {db_case.priority}.",
        event_type="milestone"
    )
    db.add(event)

    # Log Activity
    log = ActivityLog(
        action="Case Created",
        entity_type="Case",
        entity_id=db_case.id,
        details=f"Created case {db_case.case_number}: {db_case.title}"
    )
    db.add(log)
    db.commit()

    return db_case

@router.put("/{case_id}", response_model=CaseOut)
def update_case(case_id: int, case_in: CaseUpdate, db: Session = Depends(get_db)):
    db_case = db.query(Case).filter(Case.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")

    update_data = case_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case, field, value)

    db.commit()
    db.refresh(db_case)

    # Log activity
    log = ActivityLog(
        action="Case Updated",
        entity_type="Case",
        entity_id=db_case.id,
        details=f"Updated case {db_case.case_number}"
    )
    db.add(log)
    db.commit()

    return db_case

@router.get("/{case_id}/events", response_model=List[CaseEventOut])
def get_case_events(case_id: int, db: Session = Depends(get_db)):
    return db.query(CaseEvent).filter(CaseEvent.case_id == case_id).order_by(CaseEvent.event_date.desc()).all()

@router.post("/{case_id}/events", response_model=CaseEventOut, status_code=201)
def create_case_event(case_id: int, event_in: CaseEventCreate, db: Session = Depends(get_db)):
    event = CaseEvent(
        case_id=case_id,
        title=event_in.title,
        description=event_in.description,
        event_date=event_in.event_date,
        event_type=event_in.event_type
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

# ─────────────────────────────────────────────────────────────
# Case ↔ Subject Linking  (uses the Relationship table)
# ─────────────────────────────────────────────────────────────

@router.get("/{case_id}/subjects", response_model=List[SubjectOut])
def get_case_subjects(case_id: int, db: Session = Depends(get_db)):
    """Return all subjects linked to a case via the Relationship table."""
    # Verify case exists
    if not db.query(Case).filter(Case.id == case_id).first():
        raise HTTPException(status_code=404, detail="Case not found")

    links = db.query(Relationship).filter(
        Relationship.source_type == "Case",
        Relationship.source_id == case_id,
        Relationship.target_type == "Subject"
    ).all()
    subject_ids = [l.target_id for l in links]
    if not subject_ids:
        return []
    return db.query(Subject).filter(Subject.id.in_(subject_ids)).all()


@router.post("/{case_id}/subjects/{subject_id}", status_code=201)
def link_subject_to_case(
    case_id: int,
    subject_id: int,
    relation_type: str = "associated_with",
    db: Session = Depends(get_db)
):
    """Link a subject to a case. Idempotent — won't duplicate."""
    if not db.query(Case).filter(Case.id == case_id).first():
        raise HTTPException(status_code=404, detail="Case not found")
    if not db.query(Subject).filter(Subject.id == subject_id).first():
        raise HTTPException(status_code=404, detail="Subject not found")

    # Check if already linked
    existing = db.query(Relationship).filter(
        Relationship.source_type == "Case",
        Relationship.source_id == case_id,
        Relationship.target_type == "Subject",
        Relationship.target_id == subject_id
    ).first()
    if existing:
        return {"message": "Already linked", "relationship_id": existing.id}

    rel = Relationship(
        source_type="Case",
        source_id=case_id,
        target_type="Subject",
        target_id=subject_id,
        relation_type=relation_type,
        confidence=0.95
    )
    db.add(rel)

    log = ActivityLog(
        action="Subject Linked to Case",
        entity_type="Case",
        entity_id=case_id,
        details=f"Linked subject ID {subject_id} to case ID {case_id} as '{relation_type}'"
    )
    db.add(log)
    db.commit()
    db.refresh(rel)
    return {"message": "Linked successfully", "relationship_id": rel.id}


@router.delete("/{case_id}/subjects/{subject_id}", status_code=200)
def unlink_subject_from_case(case_id: int, subject_id: int, db: Session = Depends(get_db)):
    """Remove the link between a subject and a case."""
    rel = db.query(Relationship).filter(
        Relationship.source_type == "Case",
        Relationship.source_id == case_id,
        Relationship.target_type == "Subject",
        Relationship.target_id == subject_id
    ).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(rel)
    log = ActivityLog(
        action="Subject Unlinked from Case",
        entity_type="Case",
        entity_id=case_id,
        details=f"Removed subject ID {subject_id} from case ID {case_id}"
    )
    db.add(log)
    db.commit()
    return {"message": "Unlinked successfully"}


# ─────────────────────────────────────────────────────────────
# Case ↔ Case Linking  (cross-case relationships)
# ─────────────────────────────────────────────────────────────

CASE_LINK_TYPES = [
    "continuation_of", "shares_suspect", "shares_evidence",
    "parallel_investigation", "spawned_from", "financially_linked",
    "geographically_linked", "same_network", "related_operation"
]

@router.get("/{case_id}/related", response_model=List[CaseLinkOut])
def get_related_cases(case_id: int, db: Session = Depends(get_db)):
    """Get all cases linked to this case (in either direction)."""
    if not db.query(Case).filter(Case.id == case_id).first():
        raise HTTPException(status_code=404, detail="Case not found")

    results = []

    # Source → Target
    forward = db.query(Relationship).filter(
        Relationship.source_type == "Case",
        Relationship.source_id == case_id,
        Relationship.target_type == "Case"
    ).all()
    for r in forward:
        c = db.query(Case).filter(Case.id == r.target_id).first()
        if c:
            results.append(CaseLinkOut(
                id=c.id, case_number=c.case_number, title=c.title,
                category=c.category, priority=c.priority, status=c.status,
                risk_score=c.risk_score, relation_type=r.relation_type,
                relationship_id=r.id
            ))

    # Target ← Source (reverse)
    backward = db.query(Relationship).filter(
        Relationship.target_type == "Case",
        Relationship.target_id == case_id,
        Relationship.source_type == "Case"
    ).all()
    for r in backward:
        c = db.query(Case).filter(Case.id == r.source_id).first()
        if c:
            results.append(CaseLinkOut(
                id=c.id, case_number=c.case_number, title=c.title,
                category=c.category, priority=c.priority, status=c.status,
                risk_score=c.risk_score,
                relation_type=f"{r.relation_type} (↔ reverse)",
                relationship_id=r.id
            ))

    return results


@router.post("/{case_id}/related/{other_case_id}", status_code=201)
def link_cases(
    case_id: int,
    other_case_id: int,
    relation_type: str = "related_operation",
    db: Session = Depends(get_db)
):
    """Link two cases together. Idempotent — won't duplicate."""
    if case_id == other_case_id:
        raise HTTPException(status_code=400, detail="Cannot link a case to itself")
    if not db.query(Case).filter(Case.id == case_id).first():
        raise HTTPException(status_code=404, detail="Case not found")
    if not db.query(Case).filter(Case.id == other_case_id).first():
        raise HTTPException(status_code=404, detail="Related case not found")

    # Prevent duplicate (check both directions)
    existing = db.query(Relationship).filter(
        Relationship.source_type == "Case",
        Relationship.target_type == "Case",
        ((Relationship.source_id == case_id) & (Relationship.target_id == other_case_id)) |
        ((Relationship.source_id == other_case_id) & (Relationship.target_id == case_id))
    ).first()
    if existing:
        return {"message": "Already linked", "relationship_id": existing.id}

    rel = Relationship(
        source_type="Case", source_id=case_id,
        target_type="Case", target_id=other_case_id,
        relation_type=relation_type,
        confidence=0.90
    )
    db.add(rel)

    # Log both directions
    c1 = db.query(Case).filter(Case.id == case_id).first()
    c2 = db.query(Case).filter(Case.id == other_case_id).first()
    log = ActivityLog(
        action="Cases Linked",
        entity_type="Case",
        entity_id=case_id,
        details=f"Linked {c1.case_number} ↔ {c2.case_number} as '{relation_type}'"
    )
    db.add(log)
    db.commit()
    db.refresh(rel)
    return {"message": "Cases linked", "relationship_id": rel.id}


@router.delete("/{case_id}/related/{relationship_id}", status_code=200)
def unlink_cases(case_id: int, relationship_id: int, db: Session = Depends(get_db)):
    """Remove a case-to-case relationship by its relationship ID."""
    rel = db.query(Relationship).filter(
        Relationship.id == relationship_id,
        Relationship.source_type == "Case",
        Relationship.target_type == "Case"
    ).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")

    db.delete(rel)
    log = ActivityLog(
        action="Cases Unlinked",
        entity_type="Case",
        entity_id=case_id,
        details=f"Removed case relationship ID {relationship_id}"
    )
    db.add(log)
    db.commit()
    return {"message": "Cases unlinked"}
