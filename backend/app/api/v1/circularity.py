from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.circularity import CircularityInput, SustainabilityInput
from backend.app.services import circularity_service
from backend.app.lca.engine import get_ore_types

router = APIRouter(prefix="/circularity", tags=["Circular Economy"])


@router.post("/calculate")
def calculate_circularity(request: CircularityInput, db: Session = Depends(get_db)):
    result = circularity_service.calculate_circularity(
        ore_processed_tonnes=request.ore_processed_tonnes,
        waste_generated_tonnes=request.waste_generated_tonnes,
        water_used_m3=request.water_used_m3,
        energy_consumed_mj=request.energy_consumed_mj,
        recycled_material_tonnes=request.recycled_material_tonnes,
        product_output_tonnes=request.product_output_tonnes,
        facility_name=request.facility_name,
        ore_type=request.ore_type,
        db=db,
    )
    return result


@router.post("/sustainability")
def calculate_sustainability(request: SustainabilityInput, db: Session = Depends(get_db)):
    result = circularity_service.calculate_sustainability(
        carbon_kg=request.carbon_footprint_kg_co2,
        water_m3=request.water_footprint_m3,
        energy_mj=request.energy_consumption_mj,
        waste_kg=request.waste_generation_kg,
        recycling_rate=request.recycling_rate,
        community_investment_usd=request.community_investment_usd,
        employees=request.employees,
        revenue_usd=request.revenue_usd,
        facility_name=request.facility_name,
        ore_type=request.ore_type,
        db=db,
    )
    return result


@router.get("/ore-types")
def list_ore_types():
    return {"ore_types": get_ore_types()}


@router.get("/history")
def get_circularity_history(db: Session = Depends(get_db), limit: int = 50):
    return circularity_service.get_circularity_history(db, limit)


@router.get("/sustainability/history")
def get_sustainability_history(db: Session = Depends(get_db), limit: int = 50):
    return circularity_service.get_sustainability_history(db, limit)
