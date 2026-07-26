from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class DatasetCreate(BaseModel):
    name: str = Field(..., max_length=100)
    source: str = Field(default="", max_length=100)
    description: str = Field(default="")


class DatasetResponse(BaseModel):
    id: int
    name: str
    source: str
    description: str
    file_path: str
    file_size: float
    row_count: int
    column_count: int
    status: str
    preprocessed: bool
    owner_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatasetMetadataResponse(BaseModel):
    id: int
    dataset_id: int
    column_name: str
    data_type: str
    null_count: int
    null_percentage: float
    unique_count: int
    mean_value: Optional[float]
    std_value: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    description: str

    class Config:
        from_attributes = True


class DatasetStats(BaseModel):
    total_datasets: int
    total_rows: int
    total_columns: int
    preprocessed_count: int
    by_source: dict[str, int]
