"""EDASuite - Lightweight EDA library for data analysis."""

__version__ = "0.0.3"
__author__ = "LattIQ Development Team"
__email__ = "dev@lattiq.com"

from edasuite.core.exceptions import (
    AnalysisError,
    ConfigurationError,
    DataLoadError,
    DataValidationError,
    EDASuiteError,
    FeatureTypeError,
    MissingDataError,
    OutputFormattingError,
    StabilityAnalysisError,
    TargetAnalysisError,
)
from edasuite.core.loader import DataLoader
from edasuite.core.types import FeatureMetadata
from edasuite.eda import EDARunner

__all__ = [
    "EDARunner",
    # Data Loading Utilities
    "DataLoader",
    "FeatureMetadata",
    # Exceptions
    "EDASuiteError",
    "DataLoadError",
    "DataValidationError",
    "AnalysisError",
    "ConfigurationError",
    "FeatureTypeError",
    "MissingDataError",
    "StabilityAnalysisError",
    "OutputFormattingError",
    "TargetAnalysisError",
]
