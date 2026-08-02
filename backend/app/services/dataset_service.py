import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.models.dataset import Dataset, DatasetMetadata
from backend.app.pipeline.data_loader import load_all_datasets
from backend.app.utils.logger import logger
from backend.app.config import settings


_cached_datasets: dict[str, pd.DataFrame] = {}
_datasets_info_cache: list | None = None


def load_datasets() -> dict[str, pd.DataFrame]:
    global _cached_datasets
    if not _cached_datasets:
        _cached_datasets = load_all_datasets()
    return _cached_datasets


def invalidate_datasets_cache():
    global _cached_datasets, _datasets_info_cache
    _cached_datasets = {}
    _datasets_info_cache = None


def get_dataset(name: str) -> pd.DataFrame:
    datasets = load_datasets()
    return datasets.get(name, pd.DataFrame())


def get_all_dataset_names() -> list[str]:
    return [
        "mining_projects", "factory", "facilities", "commodities", "minerals",
        "coal", "processing", "waste", "transport", "reserves", "ownership",
        "capacity", "material_ids", "source_ids", "world_commodities",
        "world_companies", "commodity_info"
    ]


def get_dataset_info(name: str) -> dict:
    df = get_dataset(name)
    if df.empty:
        return {"name": name, "rows": 0, "columns": 0, "column_names": [], "status": "not_loaded"}
    return {
        "name": name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "missing_pct": {col: round(df[col].isna().mean() * 100, 2) for col in df.columns},
        "status": "loaded"
    }


def get_all_datasets_info() -> list[dict]:
    global _datasets_info_cache
    if _datasets_info_cache is None:
        _datasets_info_cache = [get_dataset_info(name) for name in get_all_dataset_names()]
    return list(_datasets_info_cache)


def register_datasets_in_db(db: Session):
    existing = {d.name for d in db.query(Dataset.name).all()}
    for name in get_all_dataset_names():
        if name not in existing:
            info = get_dataset_info(name)
            ds = Dataset(
                name=name,
                source="auto_loaded",
                row_count=info.get("rows", 0),
                column_count=info.get("columns", 0),
                status=info.get("status", "unknown"),
            )
            db.add(ds)
    db.commit()
