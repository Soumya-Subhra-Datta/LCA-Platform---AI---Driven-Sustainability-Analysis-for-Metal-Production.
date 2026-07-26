from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EnvironmentalMetricCreate(BaseModel):
    prediction_id: Optional[int] = None
    facility_name: str = ""
    project_name: str = ""
    carbon_footprint_kg_co2: float = 0.0
    water_footprint_m3: float = 0.0
    energy_consumption_mj: float = 0.0
    waste_generation_kg: float = 0.0
    land_use_m2: float = 0.0
    air_pollution_kg: float = 0.0
    acidification_kg_so2_eq: float = 0.0
    eutrophication_kg_po4_eq: float = 0.0


class EnvironmentalMetricResponse(BaseModel):
    id: int
    prediction_id: Optional[int]
    facility_name: str
    project_name: str
    carbon_footprint_kg_co2: float
    water_footprint_m3: float
    energy_consumption_mj: float
    waste_generation_kg: float
    land_use_m2: float
    air_pollution_kg: float
    acidification_kg_so2_eq: float
    eutrophication_kg_po4_eq: float
    ozone_depletion_kg_cfc11_eq: float
    photochemical_ozone_kg_c2h4_eq: float
    details: dict
    created_at: datetime

    class Config:
        from_attributes = True


class LCAInputRequest(BaseModel):
    model_config = {"protected_namespaces": ()}

    facility_name: str = ""
    project_name: str = ""
    resource_tonnes: float = Field(..., gt=0, description="Resource size in tonnes")
    grade_pct: float = Field(..., gt=0, le=100, description="Grade in percentage")
    mining_type: str = Field(default="Surface", description="Surface or Underground")
    ore_type: str = Field(default="REE", description="Type of ore/metal being processed")
    deposit_type: str = Field(default="Carbonatite")
    processing_method: str = Field(default="default")
    transport_distance_km: float = Field(default=100.0, ge=0)
