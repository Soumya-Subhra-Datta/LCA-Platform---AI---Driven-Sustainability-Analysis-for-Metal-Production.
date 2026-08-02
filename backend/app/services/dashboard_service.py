from sqlalchemy.orm import Session
from backend.app.models.prediction import Prediction
from backend.app.models.environmental import EnvironmentalMetric
from backend.app.models.circularity import CircularityMetric
from backend.app.models.sustainability import SustainabilityScore
from backend.app.models.report import Report
from backend.app.services.dataset_service import get_all_datasets_info, get_dataset
from backend.app.services.prediction_service import get_all_model_metrics
from backend.app.services.dashboard_cache import get_cached
from backend.app.utils.logger import logger


def get_dashboard_data(db: Session) -> dict:
    return get_cached(lambda: _build_dashboard_data(db))


def _build_dashboard_data(db: Session) -> dict:
    logger.info("Building dashboard data")

    dataset_info = get_all_datasets_info()
    model_metrics = get_all_model_metrics()

    prediction_count = db.query(Prediction).count()
    lca_count = db.query(EnvironmentalMetric).count()
    circularity_count = db.query(CircularityMetric).count()
    sustainability_count = db.query(SustainabilityScore).count()
    report_count = db.query(Report).count()

    recent_predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(5).all()
    recent_lca = db.query(EnvironmentalMetric).order_by(EnvironmentalMetric.created_at.desc()).limit(5).all()
    recent_sustainability = db.query(SustainabilityScore).order_by(SustainabilityScore.created_at.desc()).limit(5).all()

    mining_df = get_dataset("mining_projects")
    continent_dist = {}
    deposit_dist = {}
    if not mining_df.empty:
        if "continent" in mining_df.columns:
            continent_dist = mining_df["continent"].value_counts().to_dict()
        if "deposit_type" in mining_df.columns:
            deposit_dist = mining_df["deposit_type"].value_counts().to_dict()

    world_df = get_dataset("world_commodities")
    ree_production = []
    if not world_df.empty and "mined_raw_mat" in world_df.columns:
        ree_data = world_df[world_df["mined_raw_mat"].str.contains("Rare Earth", case=False, na=False)]
        if not ree_data.empty:
            ree_production = ree_data.to_dict(orient="records")

    return {
        "summary": {
            "total_datasets": len(dataset_info),
            "total_rows": sum(d["rows"] for d in dataset_info),
            "prediction_count": prediction_count,
            "lca_assessment_count": lca_count,
            "circularity_count": circularity_count,
            "sustainability_count": sustainability_count,
            "report_count": report_count,
        },
        "datasets": dataset_info,
        "model_metrics": model_metrics,
        "recent_activity": {
            "predictions": [
                {"id": p.id, "model": p.model_name, "result": p.prediction_result, "time": p.created_at.isoformat() if p.created_at else None}
                for p in recent_predictions
            ],
            "lca_assessments": [
                {"id": m.id, "facility": m.facility_name, "carbon": m.carbon_footprint_kg_co2, "time": m.created_at.isoformat() if m.created_at else None}
                for m in recent_lca
            ],
            "sustainability": [
                {"id": s.id, "facility": s.facility_name, "score": s.overall_score, "grade": s.grade, "time": s.created_at.isoformat() if s.created_at else None}
                for s in recent_sustainability
            ],
        },
        "mining_overview": {
            "continent_distribution": continent_dist,
            "deposit_distribution": deposit_dist,
        },
        "ree_production": ree_production,
    }


def get_activity_feed(db: Session, limit: int = 20) -> list[dict]:
    activities = []

    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    for p in preds:
        activities.append({
            "type": "prediction", "model": p.model_name,
            "time": p.created_at.isoformat() if p.created_at else None,
        })

    lcas = db.query(EnvironmentalMetric).order_by(EnvironmentalMetric.created_at.desc()).limit(limit).all()
    for m in lcas:
        activities.append({
            "type": "lca_assessment", "facility": m.facility_name,
            "time": m.created_at.isoformat() if m.created_at else None,
        })

    activities.sort(key=lambda x: x.get("time", ""), reverse=True)
    return activities[:limit]
