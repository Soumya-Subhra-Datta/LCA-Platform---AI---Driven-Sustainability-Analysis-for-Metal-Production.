import pandas as pd
import numpy as np
import json
import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.database import SessionLocal
from backend.app.models.prediction import Prediction, ModelVersion
from backend.app.ml.models.base import get_model, get_all_models, MODEL_REGISTRY, invalidate_model_cache
from backend.app.ml.explainability.shap_explainer import ExplainabilityService
from backend.app.services.dataset_service import get_dataset
from backend.app.pipeline.preprocessor import MiningProjectsPreprocessor
from backend.app.utils.logger import logger


explainer = ExplainabilityService()

_train_lock = threading.Lock()
_train_status = {
    "running": False,
    "status": "idle",
    "results": None,
    "error": None,
    "started_at": None,
    "finished_at": None,
}


def get_train_status() -> dict:
    with _train_lock:
        return dict(_train_status)


def start_training():
    with _train_lock:
        if _train_status["running"]:
            return dict(_train_status)
        _train_status.update(
            running=True,
            status="training",
            results=None,
            error=None,
            started_at=datetime.utcnow().isoformat(),
            finished_at=None,
        )
    thread = threading.Thread(target=_training_worker, daemon=True)
    thread.start()
    return get_train_status()


def _training_worker():
    db = SessionLocal()
    try:
        results = train_all_models(db)
        with _train_lock:
            _train_status.update(
                running=False,
                status="done",
                results=results,
                finished_at=datetime.utcnow().isoformat(),
            )
    except Exception as e:
        logger.exception("Background model training failed")
        with _train_lock:
            _train_status.update(
                running=False,
                status="error",
                error=str(e),
                finished_at=datetime.utcnow().isoformat(),
            )
    finally:
        db.close()


def get_available_models() -> list[dict]:
    return [
        {"name": "hree_predictor", "type": "regression", "description": "Predicts HREE percentage from geochemical features"},
        {"name": "deposit_classifier", "type": "classification", "description": "Classifies deposit type from REE composition"},
        {"name": "resource_estimator", "type": "regression", "description": "Estimates resource size from grade and composition"},
        {"name": "dy_predictor", "type": "regression", "description": "Predicts Dy2O3 content from LREE and deposit features"},
    ]


def train_all_models(db: Session) -> dict[str, dict]:
    logger.info("Training all models")
    df = get_dataset("mining_projects")
    if df.empty:
        raise ValueError("Mining projects dataset not loaded")

    preprocessor = MiningProjectsPreprocessor()
    X, y_hree = preprocessor.fit_transform(df)

    results = {}

    from backend.app.ml.models.base import HREEPredictor, DepositClassifier, ResourceEstimator, DyPredictor

    hree_model = HREEPredictor()
    results["hree_predictor"] = hree_model.train(X, y_hree)

    if "deposit_type" in df.columns:
        valid_mask = df["deposit_type"].notna() & (df.index.isin(X.index))
        y_deposit = df.loc[X.index, "deposit_type"]
        dep_model = DepositClassifier()
        results["deposit_classifier"] = dep_model.train(X, y_deposit)

    if "resource_tonnes" in df.columns:
        y_resource = df.loc[X.index, "resource_tonnes"]
        y_resource = pd.to_numeric(y_resource, errors="coerce")
        res_model = ResourceEstimator()
        results["resource_estimator"] = res_model.train(X, y_resource)

    if "Dy2O3" in df.columns:
        y_dy = df.loc[X.index, "Dy2O3"]
        dy_model = DyPredictor()
        results["dy_predictor"] = dy_model.train(X, y_dy)

    invalidate_model_cache()

    for model_name, metrics in results.items():
        mv = db.query(ModelVersion).filter(
            ModelVersion.model_name == model_name, ModelVersion.is_active == True
        ).first()
        if mv:
            mv.is_active = False

        mv_new = ModelVersion(
            model_name=model_name,
            version=datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            model_type="regression" if "r2" in metrics else "classification",
            algorithm=type(get_model(model_name)).__name__,
            metrics=metrics,
            feature_names=preprocessor.feature_names,
            is_active=True,
        )
        db.add(mv_new)
    db.commit()

    logger.info(f"All models trained: {list(results.keys())}")
    return results


def run_prediction(model_name: str, input_data: dict, user_id: int = None, db: Session = None) -> dict:
    logger.info(f"Running prediction with {model_name}")
    model = get_model(model_name)
    if model is None or model.model is None:
        raise ValueError(f"Model {model_name} not found or not trained")

    df = get_dataset("mining_projects")
    preprocessor = MiningProjectsPreprocessor()
    if preprocessor.is_fitted:
        preprocessor.load()
    else:
        _, _ = preprocessor.fit_transform(df)

    feature_values = []
    for fname in preprocessor.feature_names:
        feature_values.append(input_data.get(fname, 0))
    X = np.array(feature_values).reshape(1, -1)

    start_time = datetime.utcnow()
    if model_name == "hree_predictor":
        result = model.predict_hree(pd.DataFrame(X, columns=preprocessor.feature_names))
    elif model_name == "deposit_classifier":
        result = model.predict_deposit(pd.DataFrame(X, columns=preprocessor.feature_names))
    elif model_name == "resource_estimator":
        result = model.predict_resource(pd.DataFrame(X, columns=preprocessor.feature_names))
    elif model_name == "dy_predictor":
        result = model.predict_dy(pd.DataFrame(X, columns=preprocessor.feature_names))
    else:
        result = {"prediction": model.predict(X).tolist()}
    elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

    explanation = explainer.explain(model, pd.DataFrame(X, columns=preprocessor.feature_names), model_name, result)

    confidence = result.get("confidence", None)
    confidence_score = None
    if isinstance(confidence, str):
        confidence_score = {"high": 0.9, "medium": 0.7, "low": 0.5}.get(confidence, 0.5)
    elif isinstance(confidence, (int, float)):
        confidence_score = float(confidence)

    prediction_record = None
    if db:
        pred = Prediction(
            user_id=user_id,
            model_name=model_name,
            input_data=input_data,
            prediction_result=result,
            confidence_score=confidence_score,
            explanation=explanation,
            execution_time_ms=elapsed_ms,
        )
        db.add(pred)
        db.commit()
        db.refresh(pred)
        prediction_record = pred.id

    return {
        "prediction_id": prediction_record,
        "model_name": model_name,
        "result": result,
        "explanation": explanation,
        "execution_time_ms": round(elapsed_ms, 2),
    }


def get_model_metrics(model_name: str) -> dict:
    model = get_model(model_name)
    if model is None:
        return {}
    return model.metrics


def get_all_model_metrics() -> dict[str, dict]:
    result = {}
    for name in MODEL_REGISTRY:
        metrics = get_model_metrics(name)
        if metrics:
            result[name] = metrics
    return result
