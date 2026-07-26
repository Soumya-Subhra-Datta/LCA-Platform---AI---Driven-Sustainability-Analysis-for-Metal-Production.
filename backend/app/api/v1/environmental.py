from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.environmental import LCAInputRequest
from backend.app.services import environmental_service
from backend.app.lca.engine import get_ore_types

router = APIRouter(prefix="/environmental", tags=["Environmental / LCA"])


@router.post("/assess")
def run_lca_assessment(request: LCAInputRequest, db: Session = Depends(get_db)):
    processing_steps = ["crushing", "grinding", "leaching", "solvent_extraction"]
    if request.processing_method and request.processing_method != "default":
        processing_steps = request.processing_method.split(",")

    result = environmental_service.run_lca_assessment(
        resource_tonnes=request.resource_tonnes,
        grade_pct=request.grade_pct,
        mining_type=request.mining_type,
        processing_steps=processing_steps,
        transport_distance_km=request.transport_distance_km,
        facility_name=request.facility_name,
        project_name=request.project_name,
        ore_type=request.ore_type,
        db=db,
    )
    return result


@router.get("/ore-types")
def list_ore_types():
    return {"ore_types": get_ore_types()}


@router.get("/benchmarks")
def get_benchmarks():
    return environmental_service.get_benchmark_data()


@router.get("/history")
def get_environmental_history(db: Session = Depends(get_db), limit: int = 50):
    return environmental_service.get_environmental_history(db, limit)
