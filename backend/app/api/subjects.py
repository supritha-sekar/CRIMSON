from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Subject, ActivityLog
from app.schemas import SubjectOut, SubjectCreate, SubjectUpdate

router = APIRouter(prefix="/subjects", tags=["Subjects & Entities"])

@router.get("", response_model=List[SubjectOut])
def get_subjects(
    entity_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Subject)
    if entity_type and entity_type != "ALL":
        query = query.filter(Subject.entity_type == entity_type)
    if risk_level and risk_level != "ALL":
        query = query.filter(Subject.risk_level == risk_level)
    if search:
        query = query.filter(
            (Subject.name.ilike(f"%{search}%")) |
            (Subject.description.ilike(f"%{search}%"))
        )
    return query.order_by(Subject.updated_at.desc()).all()

@router.get("/{subject_id}", response_model=SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(subject_in: SubjectCreate, db: Session = Depends(get_db)):
    db_subject = Subject(
        name=subject_in.name,
        entity_type=subject_in.entity_type,
        description=subject_in.description,
        identifiers_json=subject_in.identifiers_json,
        notes=subject_in.notes,
        risk_level=subject_in.risk_level,
        risk_score=subject_in.risk_score
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)

    log = ActivityLog(
        action="Subject Created",
        entity_type="Subject",
        entity_id=db_subject.id,
        details=f"Added entity {db_subject.name} ({db_subject.entity_type})"
    )
    db.add(log)
    db.commit()

    return db_subject

@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, subject_in: SubjectUpdate, db: Session = Depends(get_db)):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    update_data = subject_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subject, field, value)

    db.commit()
    db.refresh(db_subject)
    return db_subject
