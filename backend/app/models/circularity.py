from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from datetime import datetime
from backend.app.database import Base


class CircularityMetric(Base):
    __tablename__ = "circularity_metrics"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    facility_name = Column(String(200), default="")
    circularity_score = Column(Float, default=0.0)
    recycling_potential = Column(Float, default=0.0)
    resource_efficiency = Column(Float, default=0.0)
    material_recovery_rate = Column(Float, default=0.0)
    waste_diversion_rate = Column(Float, default=0.0)
    secondary_material_usage = Column(Float, default=0.0)
    product_life_extension = Column(Float, default=0.0)
    recommendations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
