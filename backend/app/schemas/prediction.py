from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_name: str = Field(..., description="Model to use: hree_predictor, deposit_classifier, resource_estimator, dy_predictor")
    input_data: dict[str, Any] = Field(..., description="Input features for prediction")


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: int
    model_name: str
    input_data: dict
    prediction_result: dict
    confidence_score: Optional[float]
    explanation: dict
    execution_time_ms: float
    created_at: datetime


class BatchPredictionRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_name: str
    inputs: list[dict[str, Any]]


class ModelVersionResponse(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: int
    model_name: str
    version: str
    model_type: str
    algorithm: str
    metrics: dict
    feature_names: list
    is_active: bool
    created_at: datetime
