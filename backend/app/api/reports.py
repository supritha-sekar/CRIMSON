from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.models import Report, Case, Subject, ActivityLog
from app.schemas import ReportOut, ReportCreate
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("", response_model=List[ReportOut])
def get_reports(case_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Report)
    if case_id:
        query = query.filter(Report.case_id == case_id)
    reports = query.order_by(Report.created_at.desc()).all()

    out = []
    for r in reports:
        out.append({
            "id": r.id,
            "report_number": r.report_number,
            "title": r.title,
            "report_type": r.report_type,
            "case_id": r.case_id,
            "content": json.loads(r.content_json) if r.content_json else {},
            "author_id": r.author_id,
            "format": r.format,
            "created_at": r.created_at
        })
    return out

@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": r.id,
        "report_number": r.report_number,
        "title": r.title,
        "report_type": r.report_type,
        "case_id": r.case_id,
        "content": json.loads(r.content_json) if r.content_json else {},
        "author_id": r.author_id,
        "format": r.format,
        "created_at": r.created_at
    }

@router.post("/generate", response_model=ReportOut, status_code=201)
def generate_report(req: ReportCreate, db: Session = Depends(get_db)):
    count = db.query(Report).count() + 1
    rep_num = f"REP-2026-{count:03d}"

    case_dict = None
    if req.case_id:
        c = db.query(Case).filter(Case.id == req.case_id).first()
        if c:
            case_dict = {
                "id": c.id,
                "case_number": c.case_number,
                "title": c.title,
                "description": c.description,
                "priority": c.priority,
                "status": c.status,
                "category": c.category,
                "risk_score": c.risk_score
            }

    content = report_service.generate_report_content(report_type=req.report_type, case_data=case_dict)

    db_report = Report(
        report_number=rep_num,
        title=req.title,
        report_type=req.report_type,
        case_id=req.case_id,
        content_json=json.dumps(content),
        format=req.format or "JSON"
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    log = ActivityLog(
        action="Report Generated",
        entity_type="Report",
        entity_id=db_report.id,
        details=f"Generated report {db_report.report_number}: {db_report.title}"
    )
    db.add(log)
    db.commit()

    return {
        "id": db_report.id,
        "report_number": db_report.report_number,
        "title": db_report.title,
        "report_type": db_report.report_type,
        "case_id": db_report.case_id,
        "content": content,
        "author_id": db_report.author_id,
        "format": db_report.format,
        "created_at": db_report.created_at
    }
