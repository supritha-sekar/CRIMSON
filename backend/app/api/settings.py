from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.database import get_db
from app.models import SystemSetting
from app.schemas import SettingUpdate

router = APIRouter(prefix="/settings", tags=["System Settings"])

@router.get("")
def get_settings(db: Session = Depends(get_db)):
    settings_db = db.query(SystemSetting).all()
    out = {}
    for s in settings_db:
        out[s.key] = {"value": s.value, "description": s.description, "updated_at": s.updated_at}
    return out

@router.post("")
def update_setting(setting_in: SettingUpdate, db: Session = Depends(get_db)):
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_in.key).first()
    if not setting:
        setting = SystemSetting(key=setting_in.key, value=setting_in.value)
        db.add(setting)
    else:
        setting.value = setting_in.value
    db.commit()
    return {"message": f"Setting '{setting_in.key}' updated successfully"}
