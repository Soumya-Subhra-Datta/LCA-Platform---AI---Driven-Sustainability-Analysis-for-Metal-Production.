from sqlalchemy.orm import Session
from backend.app.models.circularity import CircularityMetric
from backend.app.models.sustainability import SustainabilityScore
from backend.app.circular.engine import CircularityCalculator, SustainabilityScorer
from backend.app.services.dashboard_cache import invalidate as invalidate_dashboard_cache
from backend.app.utils.logger import logger


circularity_calc = CircularityCalculator()
sustainability_scorer = SustainabilityScorer()


def calculate_circularity(ore_processed_tonnes: float, waste_generated_tonnes: float,
                          water_used_m3: float, energy_consumed_mj: float,
                          recycled_material_tonnes: float, product_output_tonnes: float,
                          facility_name: str = "", ore_type: str = "REE",
                          db: Session = None) -> dict:
    logger.info(f"Calculating circularity for {facility_name} ({ore_type})")

    result = circularity_calc.calculate(
        ore_processed_tonnes=ore_processed_tonnes,
        waste_generated_tonnes=waste_generated_tonnes,
        water_used_m3=water_used_m3,
        energy_consumed_mj=energy_consumed_mj,
        recycled_material_tonnes=recycled_material_tonnes,
        product_output_tonnes=product_output_tonnes,
        ore_type=ore_type,
    )

    if db:
        metric = CircularityMetric(
            facility_name=facility_name,
            circularity_score=result["circularity_score"],
            recycling_potential=result["recycling_potential"],
            resource_efficiency=result["resource_efficiency"],
            material_recovery_rate=result["material_recovery_rate"],
            waste_diversion_rate=result["waste_diversion_rate"],
            secondary_material_usage=result["secondary_material_usage"],
            product_life_extension=result["product_life_extension"],
            recommendations=result["recommendations"],
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        result["metric_id"] = metric.id
        invalidate_dashboard_cache()

    return result


def calculate_sustainability(carbon_kg: float, water_m3: float, energy_mj: float,
                             waste_kg: float, recycling_rate: float,
                             community_investment_usd: float, employees: int,
                             revenue_usd: float, facility_name: str = "",
                             ore_type: str = "REE",
                             db: Session = None) -> dict:
    logger.info(f"Calculating sustainability for {facility_name} ({ore_type})")

    result = sustainability_scorer.calculate(
        carbon_kg=carbon_kg, water_m3=water_m3, energy_mj=energy_mj,
        waste_kg=waste_kg, recycling_rate=recycling_rate,
        community_investment_usd=community_investment_usd,
        employees=employees, revenue_usd=revenue_usd,
    )

    if db:
        score = SustainabilityScore(
            facility_name=facility_name,
            overall_score=result["overall_score"],
            environmental_score=result["environmental_score"],
            social_score=result["social_score"],
            governance_score=result["governance_score"],
            economic_score=result["economic_score"],
            innovation_score=result["innovation_score"],
            grade=result["grade"],
            recommendations=result["recommendations"],
            benchmark_comparison=result["benchmark_comparison"],
        )
        db.add(score)
        db.commit()
        db.refresh(score)
        result["score_id"] = score.id
        invalidate_dashboard_cache()

    return result


def get_circularity_history(db: Session, limit: int = 50) -> list[dict]:
    metrics = db.query(CircularityMetric).order_by(CircularityMetric.created_at.desc()).limit(limit).all()
    return [
        {
            "id": m.id, "facility_name": m.facility_name,
            "circularity_score": m.circularity_score,
            "recycling_potential": m.recycling_potential,
            "resource_efficiency": m.resource_efficiency,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in metrics
    ]


def get_sustainability_history(db: Session, limit: int = 50) -> list[dict]:
    scores = db.query(SustainabilityScore).order_by(SustainabilityScore.created_at.desc()).limit(limit).all()
    return [
        {
            "id": s.id, "facility_name": s.facility_name,
            "overall_score": s.overall_score, "grade": s.grade,
            "environmental_score": s.environmental_score,
            "social_score": s.social_score,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in scores
    ]
