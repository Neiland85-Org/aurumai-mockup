"""
Domain Value Objects for AurumAI Platform

Value objects are immutable and defined by their attributes, not identity.
"""

from .measurement import Measurement, TimeSeriesPoint
from .feature_vector import FeatureVector
from .prediction import Prediction

__all__ = [
    "Measurement",
    "TimeSeriesPoint",
    "FeatureVector",
    "Prediction",
]
