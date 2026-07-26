from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CircularityInput(BaseModel):
    facility_name: str = ""
    ore_type: str = "REE"
    mining_type: str = "Surface"
    ore_processed_tonnes: float = Field(default=100000.0, gt=0)
    waste_generated_tonnes: float = Field(default=50000.0, ge=0)
    water_used_m3: float = Field(default=100000.0, ge=0)
    energy_consumed_mj: float = Field(default=500000.0, ge=0)
    recycled_material_tonnes: float = Field(default=0.0, ge=0)
    product_output_tonnes: float = Field(default=1000.0, gt=0)


class CircularityResponse(BaseModel):
    id: int
    facility_name: str
    circularity_score: float
    recycling_potential: float
    resource_efficiency: float
    material_recovery_rate: float
    waste_diversion_rate: float
    secondary_material_usage: float
    product_life_extension: float
    recommendations: list
    created_at: datetime

    class Config:
        from_attributes = True


class SustainabilityInput(BaseModel):
    model_config = {"protected_namespaces": ()}

    facility_name: str = ""
    ore_type: str = "REE"
    carbon_footprint_kg_co2: float = 0.0
    water_footprint_m3: float = 0.0
    energy_consumption_mj: float = 0.0
    waste_generation_kg: float = 0.0
    recycling_rate: float = 0.0
    community_investment_usd: float = 0.0
    employees: int = 0
    revenue_usd: float = 0.0


class SustainabilityResponse(BaseModel):
    id: int
    facility_name: str
    overall_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    economic_score: float
    innovation_score: float
    grade: str
    recommendations: list
    benchmark_comparison: dict
    created_at: datetime

    class Config:
        from_attributes = True
