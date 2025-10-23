# app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    metrics = Column(JSON, nullable=True)
    threshold = Column(Float, default=0.5)
    active = Column(Boolean, default=False)

class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    score = Column(Float, nullable=True)
    label_pred = Column(String, nullable=True)
    label_true = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class ReviewItem(Base):
    __tablename__ = "review_items"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    score = Column(Float, nullable=True)
    model_version = Column(String, nullable=True)
    status = Column(String, default="pending")
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_label = Column(String, nullable=True)
