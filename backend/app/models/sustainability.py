from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
from datetime import datetime
from backend.app.database import Base


class SustainabilityScore(Base):
    __tablename__ = "sustainability_scores"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    facility_name = Column(String(200), default="")
    overall_score = Column(Float, default=0.0)
    environmental_score = Column(Float, default=0.0)
    social_score = Column(Float, default=0.0)
    governance_score = Column(Float, default=0.0)
    economic_score = Column(Float, default=0.0)
    innovation_score = Column(Float, default=0.0)
    grade = Column(String(5), default="")
    recommendations = Column(JSON, default=list)
    benchmark_comparison = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
