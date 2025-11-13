"""Base analyzer interface and common functionality."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import pandas as pd

from edasuite.core.types import FeatureMetadata, FeatureType


@dataclass
class AnalysisResult:
    """Container for analysis results with metadata."""
    analyzer_name: str
    column_name: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "analyzer": self.analyzer_name,
            "column": self.column_name,
            "data": self.data,
            "metadata": self.metadata,
            "execution_time": self.execution_time
        }


class BaseAnalyzer(ABC):
    """Abstract base class for all data analyzers."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._feature_metadata: Optional[FeatureMetadata] = None

    @property
    @abstractmethod
    def analyzer_name(self) -> str:
        """Return the name of this analyzer."""
        pass

    @abstractmethod
    def can_analyze(self, series: pd.Series) -> bool:
        """Check if this analyzer can process the given series."""
        pass

    @abstractmethod
    def _analyze_impl(self, series: pd.Series) -> Dict[str, Any]:
        """Core analysis implementation."""
        pass

    def analyze(self, series: pd.Series, feature_metadata: Optional[FeatureMetadata] = None) -> AnalysisResult:
        """
        Main analysis method implementing the template pattern.

        Args:
            series: Pandas series to analyze
            feature_metadata: Optional feature metadata containing default/no_hit values

        Returns:
            Analysis result with processed data
        """
        start_time = time.perf_counter()

        # Store feature metadata for use in preprocessing
        self._feature_metadata = feature_metadata

        if not self.can_analyze(series):
            raise ValueError(f"{self.analyzer_name} cannot analyze series '{series.name}'")

        processed_series = self._preprocess(series)
        results = self._analyze_impl(processed_series)
        results = self._postprocess(results, processed_series)

        execution_time = time.perf_counter() - start_time

        return AnalysisResult(
            analyzer_name=self.analyzer_name,
            column_name=series.name,
            data=results,
            metadata={
                "dtype": str(series.dtype),
                "size": len(series),
                "null_count": series.isnull().sum(),
            },
            execution_time=execution_time,
        )

    def _preprocess(self, series: pd.Series) -> pd.Series:
        """
        Pre-process series before analysis.

        Converts default values and no_hit values from feature metadata to NaN
        so they are treated as missing values during analysis.

        Args:
            series: Input series to preprocess

        Returns:
            Preprocessed series with special values converted to NaN
        """
        if self._feature_metadata is None:
            return series

        # Make a copy to avoid modifying the original
        processed_series = series.copy()

        # Convert default value to NaN if specified
        if self._feature_metadata.default is not None:
            default_val = self._feature_metadata.default
            # Try to convert to appropriate type for comparison
            try:
                if pd.api.types.is_numeric_dtype(series):
                    default_val = float(default_val) if '.' in str(default_val) else int(default_val)
                mask = processed_series == default_val
                processed_series[mask] = pd.NA
            except (ValueError, TypeError):
                # If conversion fails, compare as string
                mask = processed_series.astype(str) == str(default_val)
                processed_series[mask] = pd.NA

        # Convert no_hit_value to NaN if specified
        if self._feature_metadata.no_hit_value is not None:
            no_hit_val = self._feature_metadata.no_hit_value
            # Try to convert to appropriate type for comparison
            try:
                if pd.api.types.is_numeric_dtype(series):
                    no_hit_val = float(no_hit_val) if '.' in str(no_hit_val) else int(no_hit_val)
                mask = processed_series == no_hit_val
                processed_series[mask] = pd.NA
            except (ValueError, TypeError):
                # If conversion fails, compare as string
                mask = processed_series.astype(str) == str(no_hit_val)
                processed_series[mask] = pd.NA

        return processed_series

    def _postprocess(self, results: Dict[str, Any], series: pd.Series) -> Dict[str, Any]:
        """Post-process analysis results."""
        return results

    @staticmethod
    def determine_feature_type(
        series: pd.Series,
        feature_metadata: Optional[FeatureMetadata] = None
    ) -> FeatureType:
        """
        Determine feature type from metadata or infer from data.

        This is the centralized method for feature type determination that respects
        metadata configuration and falls back to inference when metadata is unavailable.

        Args:
            series: pandas Series to analyze
            feature_metadata: Optional feature metadata with variable_type specification

        Returns:
            FeatureType enum value
        """
        # First priority: Use metadata if available
        if feature_metadata and feature_metadata.variable_type:
            metadata_type = feature_metadata.variable_type.lower()
            if metadata_type == "continuous":
                return FeatureType.CONTINUOUS
            elif metadata_type == "categorical":
                return FeatureType.CATEGORICAL
            elif metadata_type == "datetime":
                return FeatureType.DATETIME
            elif metadata_type == "text":
                return FeatureType.TEXT
            # If unknown metadata type, fall through to inference

        # Second priority: Infer from data
        return BaseAnalyzer.infer_feature_type(series)

    @staticmethod
    def infer_feature_type(series: pd.Series) -> FeatureType:
        """
        Infer the feature type from pandas series data characteristics.

        This method uses heuristics based on dtype and cardinality.
        Use determine_feature_type() instead if you have metadata available.
        """
        if pd.api.types.is_numeric_dtype(series):
            unique_ratio = series.nunique() / len(series)
            if unique_ratio < 0.05 and series.nunique() < 20:
                return FeatureType.CATEGORICAL
            return FeatureType.CONTINUOUS
        elif pd.api.types.is_datetime64_any_dtype(series):
            return FeatureType.DATETIME
        elif pd.api.types.is_object_dtype(series):
            try:
                pd.to_datetime(series.dropna().iloc[:100], format='mixed', errors='coerce')
                return FeatureType.DATETIME
            except (ValueError, TypeError, pd.errors.ParserError):
                pass

            if series.nunique() / len(series) < 0.5:
                return FeatureType.CATEGORICAL
            return FeatureType.TEXT
        else:
            return FeatureType.CATEGORICAL
