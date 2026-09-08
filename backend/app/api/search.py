from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.database import get_db
from app.models import Case, Subject, Evidence, Analysis, Report

router = APIRouter(prefix="/search", tags=["Global Intelligence Search"])

@router.get("/global")
def global_search(
    q: str = Query(..., min_length=1),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query_str = f"%{q}%"
    results = {
        "cases": [],
        "subjects": [],
        "evidence": [],
        "analyses": [],
        "reports": [],
        "total": 0
    }

    # 1. Cases
    cases = db.query(Case).filter(
        (Case.title.ilike(query_str)) |
        (Case.case_number.ilike(query_str)) |
        (Case.description.ilike(query_str)) |
        (Case.category.ilike(query_str))
    ).limit(10).all()

    for c in cases:
        results["cases"].append({
            "id": c.id,
            "title": f"{c.case_number}: {c.title}",
            "subtitle": f"Category: {c.category} | Priority: {c.priority}",
            "description": c.description[:120] + "...",
            "type": "Case",
            "url": f"/cases/{c.id}"
        })

    # 2. Subjects
    subjects = db.query(Subject).filter(
        (Subject.name.ilike(query_str)) |
        (Subject.description.ilike(query_str)) |
        (Subject.notes.ilike(query_str))
    ).limit(10).all()

    for s in subjects:
        results["subjects"].append({
            "id": s.id,
            "title": s.name,
            "subtitle": f"Type: {s.entity_type} | Risk Level: {s.risk_level}",
            "description": s.description or "No detailed description",
            "type": "Subject",
            "url": "/subjects"
        })

    # 3. Evidence
    evidence_items = db.query(Evidence).filter(
        (Evidence.title.ilike(query_str)) |
        (Evidence.evidence_number.ilike(query_str)) |
        (Evidence.description.ilike(query_str))
    ).limit(10).all()

    for e in evidence_items:
        results["evidence"].append({
            "id": e.id,
            "title": f"{e.evidence_number}: {e.title}",
            "subtitle": f"Type: {e.evidence_type} | Status: {e.status}",
            "description": e.description or "No description",
            "type": "Evidence",
            "url": "/evidence"
        })

    # 4. Analyses
    analyses = db.query(Analysis).filter(
        (Analysis.query_text.ilike(query_str)) |
        (Analysis.summary.ilike(query_str))
    ).limit(5).all()

    for a in analyses:
        results["analyses"].append({
            "id": a.id,
            "title": f"Analysis: {a.query_text[:50]}...",
            "subtitle": f"Confidence: {a.confidence_score*100:.0f}%",
            "description": a.summary[:120] + "...",
            "type": "Analysis",
            "url": "/analysis"
        })

    # 5. Reports
    reports = db.query(Report).filter(
        (Report.title.ilike(query_str)) |
        (Report.report_number.ilike(query_str))
    ).limit(5).all()

    for r in reports:
        results["reports"].append({
            "id": r.id,
            "title": f"{r.report_number}: {r.title}",
            "subtitle": f"Type: {r.report_type}",
            "description": f"Generated report format: {r.format}",
            "type": "Report",
            "url": "/reports"
        })

    results["total"] = (
        len(results["cases"]) +
        len(results["subjects"]) +
        len(results["evidence"]) +
        len(results["analyses"]) +
        len(results["reports"])
    )

    return results
