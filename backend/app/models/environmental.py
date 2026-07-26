from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base


class EnvironmentalMetric(Base):
    __tablename__ = "environmental_metrics"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    facility_name = Column(String(200), default="")
    project_name = Column(String(200), default="")
    carbon_footprint_kg_co2 = Column(Float, default=0.0)
    water_footprint_m3 = Column(Float, default=0.0)
    energy_consumption_mj = Column(Float, default=0.0)
    waste_generation_kg = Column(Float, default=0.0)
    land_use_m2 = Column(Float, default=0.0)
    air_pollution_kg = Column(Float, default=0.0)
    acidification_kg_so2_eq = Column(Float, default=0.0)
    eutrophication_kg_po4_eq = Column(Float, default=0.0)
    ozone_depletion_kg_cfc11_eq = Column(Float, default=0.0)
    photochemical_ozone_kg_c2h4_eq = Column(Float, default=0.0)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("Prediction", foreign_keys=[prediction_id])
