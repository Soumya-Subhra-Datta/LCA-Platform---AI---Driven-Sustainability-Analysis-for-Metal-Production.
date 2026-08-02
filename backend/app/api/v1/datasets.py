import json
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services import dataset_service


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj) if not np.isnan(obj) else None
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.get("/")
def list_datasets():
    return {"datasets": dataset_service.get_all_datasets_info()}


@router.get("/{name}")
def get_dataset_info(name: str):
    info = dataset_service.get_dataset_info(name)
    if info.get("status") == "not_loaded":
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")
    return info


@router.get("/{name}/sample")
def get_dataset_sample(name: str, rows: int = 10):
    df = dataset_service.get_dataset(name)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found or empty")
    sample_df = df.head(rows).replace({np.nan: None})
    records = sample_df.to_dict(orient="records")
    return {"name": name, "sample": records}


@router.get("/{name}/stats")
def get_dataset_stats(name: str):
    df = dataset_service.get_dataset(name)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found or empty")
    numeric_stats = {}
    for col in df.select_dtypes(include=["number"]).columns:
        numeric_stats[col] = {
            "mean": float(df[col].mean()) if df[col].notna().any() else None,
            "std": float(df[col].std()) if df[col].notna().sum() > 1 else None,
            "min": float(df[col].min()) if df[col].notna().any() else None,
            "max": float(df[col].max()) if df[col].notna().any() else None,
            "median": float(df[col].median()) if df[col].notna().any() else None,
        }
    return {"name": name, "numeric_stats": numeric_stats}


@router.post("/reload")
def reload_datasets():
    dataset_service.invalidate_datasets_cache()
    dataset_service.load_datasets()
    return {"message": "Datasets reloaded successfully"}
