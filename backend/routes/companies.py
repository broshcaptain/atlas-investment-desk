from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.services.company_service import get_company_overview

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/tuprs")
def read_tuprs(db: Session = Depends(get_db)):
    overview = get_company_overview(db, "TUPRS")

    if overview is None:
        raise HTTPException(
            status_code=404,
            detail="TUPRS için şirket verisi bulunamadı — yetersiz veri.",
        )

    return overview
