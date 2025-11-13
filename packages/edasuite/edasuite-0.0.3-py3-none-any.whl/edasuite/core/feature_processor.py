"""Feature analysis and processing logic."""

from typing import Any, Dict, List, Optional

import pandas as pd

from edasuite.analyzers.categorical import CategoricalAnalyzer
from edasuite.analyzers.continuous import ContinuousAnalyzer
from edasuite.analyzers.target_analysis import TargetAnalyzer
from edasuite.core.base import BaseAnalyzer
from edasuite.core.correlation import CorrelationEngine
from edasuite.core.logging_config import get_logger
from edasuite.core.schema_mapper import FeatureSchemaMapper
from edasuite.core.types import FeatureMetadata, FeatureType
from edasuite.output.formatter import safe_round

logger = get_logger(__name__)


class FeatureProcessor:
    """Handles feature analysis, quality assessment, and transformation."""

    def __init__(
        self,
        max_categories: int = 50,
        correlation_engine: Optional[CorrelationEngine] = None,
    ):
        """
        Initialize feature processor.

        Args:
            max_categories: Maximum categories for categorical analysis
            correlation_engine: Optional correlation engine instance
        """
        self.max_categories = max_categories
        self.correlation_engine = correlation_engine

        # Initialize analyzers
        self.continuous_analyzer = ContinuousAnalyzer()
        self.categorical_analyzer = CategoricalAnalyzer(max_categories)
        self.target_analyzer = TargetAnalyzer()

    def analyze_features(
        self,
        df: pd.DataFrame,
        feature_metadata_dict: Dict[str, FeatureMetadata],
        target_variable: Optional[str] = None,
        correlation_matrix: Optional[pd.DataFrame] = None,
        precomputed_correlations: Optional[Dict[str, Any]] = None,
        columns_to_analyze: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze features in the dataset.

        Args:
            df: DataFrame with all data (including metadata columns)
            feature_metadata_dict: Feature metadata dictionary
            target_variable: Name of target variable
            correlation_matrix: Precomputed correlation matrix
            precomputed_correlations: Precomputed correlation data from metadata
            columns_to_analyze: Specific columns to analyze (excludes metadata columns like time/cohort)

        Returns:
            Dictionary of analyzed features
        """
        features = {}

        # Determine which columns to analyze
        cols_to_process = columns_to_analyze if columns_to_analyze is not None else df.columns.tolist()

        for col in cols_to_process:
            # Determine feature type - use metadata if available, otherwise infer
            feature_type = self._determine_feature_type(col, df, feature_metadata_dict)

            # Get feature metadata for this column if available
            feature_metadata = feature_metadata_dict.get(col)

            # Choose appropriate analyzer and analyze
            feature_data = self._analyze_single_feature(col, df, feature_type, feature_metadata)

            if feature_data is None:
                continue

            # Mark if this is the target variable
            if col == target_variable:
                feature_data["is_target"] = True

            # Add metadata if available
            if col in feature_metadata_dict:
                self._add_feature_metadata(feature_data, feature_metadata_dict[col])

            # Add correlations for numeric features
            if self.correlation_engine:
                correlations_data = self.correlation_engine.get_feature_correlations(
                    col, correlation_matrix, precomputed_correlations, target_variable
                )
                feature_data["correlations"] = correlations_data

            # Add target relationship analysis (IV, WoE, enhanced correlations)
            if target_variable and target_variable in df.columns and col != target_variable:
                target_rel = self.target_analyzer.analyze_target_relationship(
                    df[col], df[target_variable], feature_type.value
                )
                feature_data["target_relationship"] = target_rel

            # Add quality flags
            feature_data["quality"] = self._assess_feature_quality(feature_data, df[col])

            # Transform to final output schema in a single efficient pass
            features[col] = FeatureSchemaMapper.map_to_output_schema(
                feature_data=feature_data,
                feature_name=col,
                col_position=df.columns.get_loc(col),
                col_metadata=feature_metadata,
            )

        return features

    def _determine_feature_type(
        self, col: str, df: pd.DataFrame, feature_metadata: Dict[str, FeatureMetadata]
    ) -> FeatureType:
        """
        Determine feature type from metadata or infer from data.

        Args:
            col: Column name
            df: DataFrame
            feature_metadata: Feature metadata dictionary

        Returns:
            FeatureType enum value
        """
        # Use centralized method from BaseAnalyzer
        col_metadata = feature_metadata.get(col) if feature_metadata else None
        return BaseAnalyzer.determine_feature_type(df[col], col_metadata)

    def _analyze_single_feature(
        self,
        col: str,
        df: pd.DataFrame,
        feature_type: FeatureType,
        feature_metadata: Optional[FeatureMetadata],
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a single feature using appropriate analyzer.

        Args:
            col: Column name
            df: DataFrame
            feature_type: Feature type
            col_metadata: Optional feature metadata

        Returns:
            Feature analysis result or None if cannot analyze
        """
        if feature_type == FeatureType.CONTINUOUS:
            analyzer = self.continuous_analyzer
        elif feature_type in (FeatureType.CATEGORICAL, FeatureType.DATETIME, FeatureType.TEXT):
            # Treat DATETIME and TEXT as categorical for analysis purposes
            analyzer = self.categorical_analyzer
        else:
            # Skip UNKNOWN or any other unsupported types
            return None

        # Pass metadata to can_analyze so it respects variable_type
        if analyzer.can_analyze(df[col], feature_metadata):
            result = analyzer.analyze(df[col], feature_metadata=feature_metadata)
            return result.data

        return None

    def _add_feature_metadata(self, feature_data: Dict[str, Any], metadata: FeatureMetadata) -> None:
        """
        Add metadata fields to feature data.

        Args:
            feature_data: Feature data dictionary to update
            metadata: Feature metadata
        """
        feature_data["provider"] = metadata.provider
        feature_data["description"] = metadata.description

        # Add information about special values treated as missing
        if metadata.default is not None:
            feature_data["default_value"] = metadata.default
        if metadata.no_hit_value is not None:
            feature_data["no_hit_value"] = metadata.no_hit_value

    def _assess_feature_quality(self, feature_data: Dict[str, Any], series: pd.Series) -> Dict[str, Any]:
        """
        Assess quality flags for a feature.

        Args:
            feature_data: Feature analysis data
            series: Feature series from DataFrame

        Returns:
            Quality assessment dictionary
        """
        missing_pct = feature_data.get("missing", {}).get("percent", 0)
        outlier_pct = feature_data.get("outliers", {}).get("percent", 0)
        # unique_values is now standardized in stats for both categorical and continuous
        unique_count = feature_data.get("stats", {}).get("unique_values", 0)

        # Check for low variance (for continuous features)
        has_low_variance = False
        if feature_data.get("type") == "continuous":
            stats = feature_data.get("stats", {})
            mean = stats.get("mean")
            std = stats.get("std")
            if mean is not None and std is not None and mean != 0:
                cv = abs(std / mean)  # Coefficient of variation
                has_low_variance = cv < 0.01

        # Check if constant
        is_constant = unique_count == 1

        # Determine if recommended for modeling
        recommended = not (
            missing_pct > 30  # High missing
            or has_low_variance  # Low variance
            or is_constant  # Constant
            or outlier_pct > 50  # Too many outliers
        )

        return {
            "has_high_missing": missing_pct > 30,
            "has_low_variance": has_low_variance,
            "has_outliers": outlier_pct > 0,
            "outlier_percentage": safe_round(outlier_pct, 2),
            "is_constant": is_constant,
            "recommended_for_modeling": recommended,
        }

