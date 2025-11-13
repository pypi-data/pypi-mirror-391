"""Correlation analysis engine for EDA."""

from typing import Any, Dict, List, Optional

import pandas as pd

from edasuite.core.logging_config import get_logger
from edasuite.output.formatter import safe_round

logger = get_logger(__name__)


class CorrelationEngine:
    """Handles correlation computation and analysis for features."""

    def __init__(self, top_correlations: int = 10, max_correlation_features: Optional[int] = None):
        """
        Initialize correlation engine.

        Args:
            top_correlations: Number of top correlations to show per feature
            max_correlation_features: Maximum features for correlation matrix. None = no limit
        """
        self.top_correlations = top_correlations
        self.max_correlation_features = max_correlation_features

    def compute_correlation_matrix(
        self, df: pd.DataFrame, target_variable: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Compute correlation matrix for numeric features.

        Args:
            df: Input dataframe
            target_variable: Optional target variable to include

        Returns:
            Correlation matrix as DataFrame or None if no numeric features
        """
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if not numeric_cols:
            logger.warning("No numeric columns found for correlation calculation")
            return None

        # If max_correlation_features is set, select features based on target correlation
        if self.max_correlation_features and len(numeric_cols) > self.max_correlation_features:
            numeric_cols = self._select_correlated_features(
                df, numeric_cols, target_variable, self.max_correlation_features
            )

        logger.info(f"Computing correlation matrix for {len(numeric_cols)} numeric features")
        return df[numeric_cols].corr()

    def _select_correlated_features(
        self,
        df: pd.DataFrame,
        numeric_cols: List[str],
        target_variable: Optional[str],
        max_features: int,
    ) -> List[str]:
        """
        Select top features based on correlation with target.

        Args:
            df: Input dataframe
            numeric_cols: List of numeric column names
            target_variable: Target variable name
            max_features: Maximum number of features to select

        Returns:
            List of selected feature names
        """
        if not target_variable or target_variable not in numeric_cols:
            logger.info(
                f"No valid target variable for correlation selection. Using first {max_features} numeric features."
            )
            return numeric_cols[:max_features]

        # Compute correlations with target
        target_corr = df[numeric_cols].corrwith(df[target_variable]).abs()

        # Always include target variable
        top_features = [target_variable]

        # Select top correlated features (excluding target itself)
        other_features = target_corr.drop(target_variable, errors="ignore").nlargest(
            max_features - 1
        )
        top_features.extend(other_features.index.tolist())

        logger.info(
            f"Selected {len(top_features)} features with highest correlation to target '{target_variable}'"
        )
        return top_features

    def get_feature_correlations(
        self,
        feature_name: str,
        correlation_matrix: Optional[pd.DataFrame],
        precomputed_correlations: Optional[Dict[str, Any]],
        target_variable: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get correlation information for a feature.

        Args:
            feature_name: Name of the feature
            correlation_matrix: Precomputed correlation matrix
            precomputed_correlations: Precomputed correlation data
            target_variable: Optional target variable name

        Returns:
            Dictionary with correlation data or None
        """
        # Try precomputed correlations first (from feature metadata)
        if precomputed_correlations:
            result = self._get_precomputed_correlations(
                feature_name, precomputed_correlations, target_variable
            )
            if result is not None:
                return {"top_correlated_features": result}

        # Fall back to computed correlations
        if correlation_matrix is not None and feature_name in correlation_matrix.columns:
            correlations = self._compute_feature_correlations(
                feature_name, correlation_matrix, target_variable
            )
            return {"top_correlated_features": correlations}

        return None

    def _get_precomputed_correlations(
        self,
        feature_name: str,
        precomputed_correlations: Dict[str, Any],
        target_variable: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get precomputed correlations from metadata.

        Args:
            feature_name: Name of the feature
            precomputed_correlations: Dictionary of precomputed correlations
            target_variable: Optional target variable name

        Returns:
            List of correlation dictionaries sorted by absolute value (high to low) or None if not found
        """
        if feature_name not in precomputed_correlations:
            return None

        feature_corr = precomputed_correlations[feature_name]

        # Check if it has the expected structure
        if not isinstance(feature_corr, dict):
            return None

        correlations = []

        # Add target correlation if available and target is specified
        if target_variable and "target_correlation" in feature_corr:
            correlations.append(
                {
                    "feature": target_variable,
                    "correlation": safe_round(feature_corr["target_correlation"], 4),
                }
            )

        # Add top correlations if available
        if "top_correlations" in feature_corr:
            top_corr = feature_corr["top_correlations"]
            if isinstance(top_corr, list):
                correlations.extend(top_corr)
            elif isinstance(top_corr, dict):
                # Convert dict format to list format
                for feat, corr_val in top_corr.items():
                    if feat != feature_name:  # Exclude self-correlation
                        correlations.append({"feature": feat, "correlation": safe_round(corr_val, 4)})

        # Sort by absolute value of correlation (high to low), preserving the sign
        correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return correlations if correlations else None

    def _compute_feature_correlations(
        self, feature_name: str, correlation_matrix: pd.DataFrame, target_variable: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Compute correlations for a feature from correlation matrix.

        Args:
            feature_name: Name of the feature
            correlation_matrix: Precomputed correlation matrix
            target_variable: Optional target variable name

        Returns:
            List of top correlations sorted by absolute value (high to low), preserving sign
        """
        # Get all correlations for this feature (excluding self)
        feature_corr = correlation_matrix[feature_name].drop(feature_name, errors="ignore")

        # Remove NaN values
        feature_corr = feature_corr.dropna()

        # Get top correlations by absolute value (sorted high to low)
        top_corr = feature_corr.abs().nlargest(self.top_correlations)

        correlations = []
        for feat in top_corr.index:
            # Keep original sign of correlation
            original_corr = correlation_matrix.loc[feat, feature_name]
            correlations.append({"feature": feat, "correlation": safe_round(original_corr, 4)})

        # Already sorted by absolute value from nlargest(), but ensuring it's explicit
        # This maintains high to low order by absolute value while preserving signs
        return correlations
