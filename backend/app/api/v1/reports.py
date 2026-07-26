from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate")
def generate_report(report_type: str, title: str, db: Session = Depends(get_db)):
    result = report_service.generate_report(user_id=1, report_type=report_type, title=title, db=db)
    return result


@router.get("/")
def list_reports(db: Session = Depends(get_db)):
    return {"reports": report_service.get_reports(user_id=1, db=db)}


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = report_service.get_report(report_id, db)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
