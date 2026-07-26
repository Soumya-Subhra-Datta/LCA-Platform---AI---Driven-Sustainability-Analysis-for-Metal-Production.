from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services import dashboard_service
from backend.app.services import data_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_data(db)


@router.get("/activity")
def get_activity(db: Session = Depends(get_db), limit: int = 20):
    return {"activities": dashboard_service.get_activity_feed(db, limit)}


@router.get("/data-counts")
def get_data_counts(db: Session = Depends(get_db)):
    return data_service.clear_all_data(db, confirm=False)


@router.post("/clear-all")
def clear_all_data(db: Session = Depends(get_db)):
    return data_service.clear_all_data(db, confirm=True)


@router.post("/clear/predictions")
def clear_predictions(db: Session = Depends(get_db)):
    return data_service.clear_predictions(db)


@router.post("/clear/lca")
def clear_lca(db: Session = Depends(get_db)):
    return data_service.clear_lca(db)


@router.post("/clear/circularity")
def clear_circularity(db: Session = Depends(get_db)):
    return data_service.clear_circularity(db)


@router.post("/clear/models")
def clear_models(db: Session = Depends(get_db)):
    return data_service.clear_models(db)
