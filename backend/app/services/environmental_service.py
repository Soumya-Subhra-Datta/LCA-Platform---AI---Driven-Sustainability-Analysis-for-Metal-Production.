from sqlalchemy.orm import Session
from backend.app.models.environmental import EnvironmentalMetric
from backend.app.lca.engine import LCAEngine
from backend.app.services.dataset_service import get_dataset
from backend.app.utils.logger import logger


lca_engine = LCAEngine()


def run_lca_assessment(resource_tonnes: float, grade_pct: float, mining_type: str,
                       processing_steps: list[str], transport_distance_km: float = 0,
                       ore_mined_tonnes: float = 0, facility_name: str = "",
                       project_name: str = "", ore_type: str = "REE",
                       db: Session = None) -> dict:
    logger.info(f"Running LCA for {facility_name or project_name} ({ore_type})")

    result = lca_engine.full_assessment(
        resource_tonnes=resource_tonnes,
        grade_pct=grade_pct,
        mining_type=mining_type,
        processing_steps=processing_steps,
        transport_distance_km=transport_distance_km,
        ore_mined_tonnes=ore_mined_tonnes,
        ore_type=ore_type,
    )

    if db:
        metric = EnvironmentalMetric(
            facility_name=facility_name,
            project_name=project_name,
            carbon_footprint_kg_co2=result["carbon_footprint"]["total_kg_co2"],
            water_footprint_m3=result["water_footprint"]["total_m3"],
            energy_consumption_mj=result["energy_consumption"]["total_mj"],
            waste_generation_kg=result["waste_generation"]["total_kg"],
            acidification_kg_so2_eq=result["acidification"]["total_kg_so2_eq"],
            details=result,
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        result["metric_id"] = metric.id

    return result


def get_benchmark_data() -> dict:
    waste_df = get_dataset("waste")
    commodities_df = get_dataset("commodities")

    benchmarks = {
        "mining": {
            "avg_waste_ratio_surface": 5.0,
            "avg_waste_ratio_underground": 3.0,
            "avg_carbon_intensity_kg_co2_per_t": 15.0,
        },
        "processing": {
            "avg_recovery_rate": 0.75,
            "avg_energy_mj_per_t": 200.0,
        },
        "industry": {
            "REE_carbon_footprint_kg_per_kg": 12.5,
            "REE_water_m3_per_kg": 0.025,
            "REE_energy_mj_per_kg": 180.0,
        }
    }

    if not waste_df.empty and "stripping_ratio" in waste_df.columns:
        sr = waste_df["stripping_ratio"].dropna()
        if len(sr) > 0:
            benchmarks["mining"]["actual_avg_stripping_ratio"] = round(float(sr.mean()), 2)

    if not commodities_df.empty and "recovery_rate" in commodities_df.columns:
        rr = commodities_df["recovery_rate"].dropna()
        if len(rr) > 0:
            benchmarks["processing"]["actual_avg_recovery_rate"] = round(float(rr.mean()), 4)

    return benchmarks


def get_environmental_history(db: Session, limit: int = 50) -> list[dict]:
    metrics = db.query(EnvironmentalMetric).order_by(EnvironmentalMetric.created_at.desc()).limit(limit).all()
    return [
        {
            "id": m.id,
            "facility_name": m.facility_name,
            "project_name": m.project_name,
            "carbon_footprint_kg_co2": m.carbon_footprint_kg_co2,
            "water_footprint_m3": m.water_footprint_m3,
            "energy_consumption_mj": m.energy_consumption_mj,
            "waste_generation_kg": m.waste_generation_kg,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in metrics
    ]
