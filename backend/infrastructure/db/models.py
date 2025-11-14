"""
SQLAlchemy ORM Models for PostgreSQL + TimescaleDB
"""
from datetime import datetime
from typing import Dict
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from .postgres_config import Base


class MachineModel(Base):
    """Machine entity - equipment being monitored"""
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), unique=True, nullable=False, index=True)
    machine_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    operational = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    measurements = relationship("RawMeasurementModel", back_populates="machine", cascade="all, delete-orphan")
    features = relationship("FeatureModel", back_populates="machine", cascade="all, delete-orphan")
    predictions = relationship("PredictionModel", back_populates="machine", cascade="all, delete-orphan")
    esg_records = relationship("ESGRecordModel", back_populates="machine", cascade="all, delete-orphan")


class RawMeasurementModel(Base):
    """Raw telemetry measurements from IoT devices"""
    __tablename__ = "raw_measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    metrics = Column(JSON, nullable=False)  # Stores dict of metric_name -> value
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    machine = relationship("MachineModel", back_populates="measurements")


class FeatureModel(Base):
    """Engineered features from edge processing"""
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    features = Column(JSON, nullable=False)  # Stores dict of feature_name -> value
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    machine = relationship("MachineModel", back_populates="features")


class PredictionModel(Base):
    """ML predictions for predictive maintenance"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    failure_probability = Column(Float, nullable=False)
    maintenance_hours = Column(Integer, nullable=False)
    failure_type = Column(String(100))
    confidence = Column(Float)
    model_version = Column(String(50))
    features_used = Column(JSON)  # Which features were used for this prediction
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    machine = relationship("MachineModel", back_populates="predictions")


class ESGRecordModel(Base):
    """ESG/Carbon emissions records"""
    __tablename__ = "esg_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    instant_co2eq_kg = Column(Float, nullable=False)
    cumulative_co2eq_kg = Column(Float, nullable=False)
    fuel_rate_lh = Column(Float)
    power_consumption_kw = Column(Float)
    efficiency_score = Column(Float)
    # Note: 'metadata' is a reserved attribute name in SQLAlchemy declarative
    # Use a different attribute name while keeping the column name as 'metadata'
    metadata_json = Column("metadata", JSON)  # Additional ESG-related metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    machine = relationship("MachineModel", back_populates="esg_records")


class AlertModel(Base):
    """Alerts generated from anomalies or predictions"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.machine_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # anomaly, prediction, threshold, esg
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    # Avoid reserved attribute name 'metadata' in declarative models
    metadata_json = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
