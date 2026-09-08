from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import ActivityLog
from app.schemas import ActivityLogOut

router = APIRouter(prefix="/activity", tags=["Activity & Audit Logs"])

@router.get("", response_model=List[ActivityLogOut])
def get_activity_logs(
    limit: int = Query(50, le=200),
    action: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ActivityLog)
    if action:
        query = query.filter(ActivityLog.action.ilike(f"%{action}%"))
    return query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
