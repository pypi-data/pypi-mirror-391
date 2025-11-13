"""Basic statistics analyzer for dataset overview."""

from typing import Any, Dict

import pandas as pd

from edasuite.core.base import BaseAnalyzer
from edasuite.core.types import DatasetInfo, FeatureType


class BasicStatsAnalyzer(BaseAnalyzer):
    """Analyzer for basic dataset statistics and overview."""

    @property
    def analyzer_name(self) -> str:
        return "basic_stats"

    def can_analyze(self, series: pd.Series) -> bool:
        """BasicStatsAnalyzer works on entire DataFrame, not series."""
        return False

    def _analyze_impl(self, series: pd.Series) -> Dict[str, Any]:
        """Not used for BasicStatsAnalyzer."""
        pass

    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        feature_metadata_dict: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze entire DataFrame for basic statistics.

        Args:
            df: DataFrame to analyze
            feature_metadata: Optional dict mapping feature names to FeatureMetadata

        Returns:
            Dictionary with dataset overview
        """
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()

        dataset_info = DatasetInfo(
            rows=len(df),
            columns=len(df.columns),
            memory_mb=df.memory_usage(deep=True).sum() / 1024 / 1024,
            missing_cells=missing_cells,
            missing_percentage=(missing_cells / total_cells * 100) if total_cells > 0 else 0,
            duplicate_rows=df.duplicated().sum()
        )

        # Analyze feature types - use metadata if available
        feature_types = {}
        feature_metadata_dict = feature_metadata_dict or {}
        for col in df.columns:
            feature_metadata = feature_metadata_dict.get(col)
            feature_types[col] = self.determine_feature_type(df[col], feature_metadata)

        # Count by type
        type_counts = {
            "continuous": sum(1 for t in feature_types.values() if t == FeatureType.CONTINUOUS),
            "categorical": sum(1 for t in feature_types.values() if t == FeatureType.CATEGORICAL),
            "datetime": sum(1 for t in feature_types.values() if t == FeatureType.DATETIME),
            "text": sum(1 for t in feature_types.values() if t == FeatureType.TEXT),
        }

        return {
            "dataset_info": {
                "rows": int(dataset_info.rows),
                "columns": int(dataset_info.columns),
                "memory_mb": round(dataset_info.memory_mb, 2),
                "missing_cells": int(dataset_info.missing_cells),
                "missing_percentage": round(dataset_info.missing_percentage, 2),
                "duplicate_rows": int(dataset_info.duplicate_rows)
            },
            "feature_types": type_counts,
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
