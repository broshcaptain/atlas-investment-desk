from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services.dashboard_service import get_market_summary

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def read_dashboard(db: Session = Depends(get_db)):
    return get_market_summary(db)
