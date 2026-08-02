from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest
from backend.app.services import prediction_service

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("/models")
def list_models():
    return {"models": prediction_service.get_available_models()}


@router.post("/train")
def train_models(db: Session = Depends(get_db)):
    status = prediction_service.start_training()
    return {
        "message": "Model training started in background",
        "status": status,
        "results": status.get("results") or {},
    }


@router.get("/train-status")
def get_train_status():
    return prediction_service.get_train_status()


@router.post("/predict")
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    try:
        result = prediction_service.run_prediction(
            model_name=request.model_name,
            input_data=request.input_data,
            db=db,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch")
def batch_predict(request: BatchPredictionRequest, db: Session = Depends(get_db)):
    results = []
    for i, inp in enumerate(request.inputs):
        try:
            result = prediction_service.run_prediction(
                model_name=request.model_name,
                input_data=inp,
                db=db,
            )
            results.append({"index": i, "status": "success", "result": result})
        except Exception as e:
            results.append({"index": i, "status": "error", "error": str(e)})
    return {"model": request.model_name, "results": results}


@router.get("/metrics")
def get_model_metrics():
    return prediction_service.get_all_model_metrics()


@router.get("/metrics/{model_name}")
def get_specific_model_metrics(model_name: str):
    metrics = prediction_service.get_model_metrics(model_name)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' metrics not found")
    return {"model": model_name, "metrics": metrics}


@router.get("/history")
def get_prediction_history(db: Session = Depends(get_db), limit: int = 50):
    from backend.app.models.prediction import Prediction
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    return {"predictions": [
        {
            "id": p.id, "model_name": p.model_name, "result": p.prediction_result,
            "confidence": p.confidence_score, "time": p.created_at.isoformat() if p.created_at else None,
        }
        for p in preds
    ]}
