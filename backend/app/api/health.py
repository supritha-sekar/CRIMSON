from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter(tags=["System Health"])

@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    db_status = "ONLINE"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "DEGRADED"

    return {
        "status": "ok",
        "version": settings.VERSION,
        "database": True if db_status == "ONLINE" else False,
        "ai": True,
        "nlp": True,
        "mode": "demo",
        "services": {
            "api": "ONLINE",
            "database": db_status,
            "ai": "DEMO",
            "nlp": "DEMO"
        }
    }
