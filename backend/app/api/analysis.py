from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.models import Analysis, Case, Subject, ActivityLog, Notification
from app.schemas import AnalysisOut, AnalysisRequest, RiskAssessmentResult
from app.services.ai_engine import local_ai_engine
from app.services.risk_engine import risk_engine

router = APIRouter(prefix="/analysis", tags=["AI & Risk Analysis"])

@router.post("/run", response_model=AnalysisOut)
def run_analysis(req: AnalysisRequest, db: Session = Depends(get_db)):
    case_title = None
    if req.case_id:
        case = db.query(Case).filter(Case.id == req.case_id).first()
        if case:
            case_title = case.title

    subject_name = None
    if req.subject_id:
        subject = db.query(Subject).filter(Subject.id == req.subject_id).first()
        if subject:
            subject_name = subject.name

    # Execute Local AI Analysis
    result = local_ai_engine.analyze(
        query_text=req.query_text,
        context_text=req.context_text or "",
        case_title=case_title,
        subject_name=subject_name
    )

    # Save Analysis to DB
    db_analysis = Analysis(
        case_id=req.case_id,
        query_text=req.query_text,
        context_text=req.context_text,
        subject_id=req.subject_id,
        summary=result["summary"],
        key_findings_json=json.dumps(result["key_findings"]),
        entities_json=json.dumps(result["entities"]),
        relationships_json=json.dumps(result["relationships"]),
        risk_indicators_json=json.dumps(result["risk_indicators"]),
        confidence_score=result["confidence_score"],
        recommendations_json=json.dumps(result["recommendations"]),
        next_steps_json=json.dumps(result["next_steps"]),
        is_demo=True
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    # Log Activity
    log = ActivityLog(
        action="Analysis Executed",
        entity_type="Analysis",
        entity_id=db_analysis.id,
        details=f"Ran DEMO AI Analysis on query '{req.query_text[:40]}...'"
    )
    db.add(log)

    # Notification
    notif = Notification(
        title="AI Analysis Completed",
        message=f"DEMO AI intelligence extraction completed with {result['confidence_score']*100:.0f}% confidence score.",
        notification_type="SUCCESS",
        link="/analysis"
    )
    db.add(notif)
    db.commit()

    # Format return
    return {
        "id": db_analysis.id,
        "case_id": db_analysis.case_id,
        "query_text": db_analysis.query_text,
        "context_text": db_analysis.context_text,
        "subject_id": db_analysis.subject_id,
        "summary": result["summary"],
        "key_findings": result["key_findings"],
        "entities": result["entities"],
        "relationships": result["relationships"],
        "risk_indicators": result["risk_indicators"],
        "confidence_score": result["confidence_score"],
        "recommendations": result["recommendations"],
        "next_steps": result["next_steps"],
        "is_demo": True,
        "created_at": db_analysis.created_at
    }

@router.get("/history", response_model=List[AnalysisOut])
def get_analysis_history(case_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Analysis)
    if case_id:
        query = query.filter(Analysis.case_id == case_id)
    analyses = query.order_by(Analysis.created_at.desc()).all()
    
    out = []
    for a in analyses:
        out.append({
            "id": a.id,
            "case_id": a.case_id,
            "query_text": a.query_text,
            "context_text": a.context_text,
            "subject_id": a.subject_id,
            "summary": a.summary,
            "key_findings": json.loads(a.key_findings_json) if a.key_findings_json else [],
            "entities": json.loads(a.entities_json) if a.entities_json else [],
            "relationships": json.loads(a.relationships_json) if a.relationships_json else [],
            "risk_indicators": json.loads(a.risk_indicators_json) if a.risk_indicators_json else [],
            "confidence_score": a.confidence_score,
            "recommendations": json.loads(a.recommendations_json) if a.recommendations_json else [],
            "next_steps": json.loads(a.next_steps_json) if a.next_steps_json else [],
            "is_demo": a.is_demo,
            "created_at": a.created_at
        })
    return out

@router.post("/risk-assess", response_model=RiskAssessmentResult)
def assess_risk(
    case_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    priority = "MEDIUM"
    status = "INVESTIGATING"
    entity_count = 2
    evidence_count = 1
    flags = ["Offshore Crypto", "C2 Beaconing"]

    if case_id:
        case = db.query(Case).filter(Case.id == case_id).first()
        if case:
            priority = case.priority
            status = case.status
            evidence_count = len(case.evidence_items)

    if subject_id:
        subj = db.query(Subject).filter(Subject.id == subject_id).first()
        if subj:
            if subj.risk_level == "CRITICAL":
                flags.append("Critical Threat Subject")

    result = risk_engine.calculate_risk(
        priority=priority,
        status=status,
        entity_count=entity_count,
        evidence_count=evidence_count,
        critical_flags=flags
    )
    return result
