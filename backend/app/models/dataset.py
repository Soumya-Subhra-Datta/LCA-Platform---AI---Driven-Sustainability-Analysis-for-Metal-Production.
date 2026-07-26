from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source = Column(String(100), default="")
    description = Column(Text, default="")
    file_path = Column(String(500), default="")
    file_size = Column(Float, default=0.0)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    status = Column(String(20), default="uploaded")
    preprocessed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="datasets")
    metadata_entries = relationship("DatasetMetadata", back_populates="dataset", cascade="all, delete-orphan")


class DatasetMetadata(Base):
    __tablename__ = "dataset_metadata"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    column_name = Column(String(100), nullable=False)
    data_type = Column(String(50), default="")
    null_count = Column(Integer, default=0)
    null_percentage = Column(Float, default=0.0)
    unique_count = Column(Integer, default=0)
    mean_value = Column(Float, nullable=True)
    std_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="metadata_entries")
