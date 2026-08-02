from sqlalchemy.orm import Session
from backend.app.models.prediction import Prediction, ModelVersion
from backend.app.models.environmental import EnvironmentalMetric
from backend.app.models.circularity import CircularityMetric
from backend.app.models.sustainability import SustainabilityScore
from backend.app.models.report import Report
from backend.app.models.audit import AuditLog
from backend.app.services.dashboard_cache import invalidate as invalidate_dashboard_cache
from backend.app.utils.logger import logger


def clear_all_data(db: Session, confirm: bool = False) -> dict:
    if not confirm:
        counts = {
            "predictions": db.query(Prediction).count(),
            "model_versions": db.query(ModelVersion).count(),
            "environmental_metrics": db.query(EnvironmentalMetric).count(),
            "circularity_metrics": db.query(CircularityMetric).count(),
            "sustainability_scores": db.query(SustainabilityScore).count(),
            "reports": db.query(Report).count(),
            "audit_logs": db.query(AuditLog).count(),
        }
        total = sum(counts.values())
        return {"status": "preview", "counts": counts, "total": total,
                "message": "Pass confirm=true to delete all data"}

    logger.info("Clearing all analysis data")

    n_predictions = db.query(Prediction).delete()
    n_model_versions = db.query(ModelVersion).delete()
    n_environmental = db.query(EnvironmentalMetric).delete()
    n_circularity = db.query(CircularityMetric).delete()
    n_sustainability = db.query(SustainabilityScore).delete()
    n_reports = db.query(Report).delete()
    n_audit = db.query(AuditLog).delete()

    db.commit()
    invalidate_dashboard_cache()

    deleted = {
        "predictions": n_predictions,
        "model_versions": n_model_versions,
        "environmental_metrics": n_environmental,
        "circularity_metrics": n_circularity,
        "sustainability_scores": n_sustainability,
        "reports": n_reports,
        "audit_logs": n_audit,
    }
    total = sum(deleted.values())
    logger.info(f"Cleared {total} records total")
    return {"status": "cleared", "deleted": deleted, "total": total,
            "message": f"Successfully deleted {total} records"}


def clear_predictions(db: Session) -> dict:
    n = db.query(Prediction).delete()
    db.commit()
    invalidate_dashboard_cache()
    return {"deleted": n}


def clear_lca(db: Session) -> dict:
    n = db.query(EnvironmentalMetric).delete()
    db.commit()
    invalidate_dashboard_cache()
    return {"deleted": n}


def clear_circularity(db: Session) -> dict:
    n1 = db.query(CircularityMetric).delete()
    n2 = db.query(SustainabilityScore).delete()
    db.commit()
    invalidate_dashboard_cache()
    return {"deleted": n1 + n2}


def clear_models(db: Session) -> dict:
    n = db.query(ModelVersion).delete()
    db.commit()
    invalidate_dashboard_cache()
    return {"deleted": n}
