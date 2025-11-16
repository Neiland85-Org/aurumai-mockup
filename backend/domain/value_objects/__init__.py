"""
Domain Value Objects for AurumAI Platform

Value objects are immutable and defined by their attributes, not identity.
"""

from .feature_vector import FeatureVector
from .measurement import Measurement, TimeSeriesPoint
from .prediction import Prediction

__all__ = [
    "FeatureVector",
    "Measurement",
    "Prediction",
    "TimeSeriesPoint",
]
