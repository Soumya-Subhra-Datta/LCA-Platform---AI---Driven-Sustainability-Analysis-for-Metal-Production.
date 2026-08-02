from sqlalchemy.orm import Session
from backend.app.models.report import Report
from backend.app.models.prediction import Prediction
from backend.app.models.environmental import EnvironmentalMetric
from backend.app.models.circularity import CircularityMetric
from backend.app.models.sustainability import SustainabilityScore
from backend.app.services.dashboard_cache import invalidate as invalidate_dashboard_cache
from backend.app.utils.logger import logger
import json
from datetime import datetime


def generate_report(user_id: int, report_type: str, title: str, db: Session) -> dict:
    logger.info(f"Generating {report_type} report")

    if report_type == "lca_summary":
        content = _build_lca_summary(db)
    elif report_type == "sustainability":
        content = _build_sustainability_summary(db)
    elif report_type == "predictions":
        content = _build_predictions_summary(db)
    elif report_type == "comprehensive":
        content = _build_comprehensive_report(db)
    else:
        content = {"error": f"Unknown report type: {report_type}"}

    report = Report(
        user_id=user_id,
        title=title,
        report_type=report_type,
        content=content,
        status="generated",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    invalidate_dashboard_cache()

    return {
        "report_id": report.id,
        "title": title,
        "type": report_type,
        "content": content,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


def _build_lca_summary(db: Session) -> dict:
    metrics = db.query(EnvironmentalMetric).order_by(EnvironmentalMetric.created_at.desc()).limit(100).all()
    if not metrics:
        return {"message": "No LCA assessments found", "assessments": []}

    total_carbon = sum(m.carbon_footprint_kg_co2 for m in metrics)
    total_water = sum(m.water_footprint_m3 for m in metrics)
    total_energy = sum(m.energy_consumption_mj for m in metrics)
    total_waste = sum(m.waste_generation_kg for m in metrics)

    return {
        "assessment_count": len(metrics),
        "totals": {
            "carbon_kg_co2": round(total_carbon, 2),
            "water_m3": round(total_water, 2),
            "energy_mj": round(total_energy, 2),
            "waste_kg": round(total_waste, 2),
        },
        "averages": {
            "carbon_kg_co2": round(total_carbon / len(metrics), 2),
            "water_m3": round(total_water / len(metrics), 2),
            "energy_mj": round(total_energy / len(metrics), 2),
            "waste_kg": round(total_waste / len(metrics), 2),
        },
        "recent_assessments": [
            {
                "facility": m.facility_name or m.project_name,
                "carbon": m.carbon_footprint_kg_co2,
                "water": m.water_footprint_m3,
            }
            for m in metrics[:10]
        ]
    }


def _build_sustainability_summary(db: Session) -> dict:
    scores = db.query(SustainabilityScore).order_by(SustainabilityScore.created_at.desc()).limit(100).all()
    if not scores:
        return {"message": "No sustainability scores found", "scores": []}

    avg_overall = sum(s.overall_score for s in scores) / len(scores)
    grades = {}
    for s in scores:
        grades[s.grade] = grades.get(s.grade, 0) + 1

    return {
        "score_count": len(scores),
        "average_overall_score": round(avg_overall, 2),
        "grade_distribution": grades,
        "top_performers": [
            {"facility": s.facility_name, "score": s.overall_score, "grade": s.grade}
            for s in sorted(scores, key=lambda x: x.overall_score, reverse=True)[:5]
        ]
    }


def _build_predictions_summary(db: Session) -> dict:
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(100).all()
    if not preds:
        return {"message": "No predictions found", "predictions": []}

    model_counts = {}
    for p in preds:
        model_counts[p.model_name] = model_counts.get(p.model_name, 0) + 1

    return {
        "prediction_count": len(preds),
        "model_usage": model_counts,
        "recent_predictions": [
            {
                "model": p.model_name,
                "result": p.prediction_result,
                "confidence": p.confidence_score,
                "time": p.created_at.isoformat() if p.created_at else None,
            }
            for p in preds[:10]
        ]
    }


def _build_comprehensive_report(db: Session) -> dict:
    return {
        "lca_summary": _build_lca_summary(db),
        "sustainability_summary": _build_sustainability_summary(db),
        "predictions_summary": _build_predictions_summary(db),
        "generated_at": datetime.utcnow().isoformat(),
    }


def get_reports(user_id: int, db: Session) -> list[dict]:
    reports = db.query(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()).all()
    return [
        {
            "id": r.id, "title": r.title, "type": r.report_type,
            "status": r.status, "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]


def get_report(report_id: int, db: Session) -> dict | None:
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        return None
    return {
        "id": r.id, "title": r.title, "type": r.report_type,
        "content": r.content, "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
