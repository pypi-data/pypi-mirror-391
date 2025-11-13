"""Schema mapping utilities for transforming analyzer output to final schema."""

from datetime import datetime
from typing import Any, Dict, Optional

from edasuite.core.types import FeatureMetadata


class FeatureSchemaMapper:
    """Maps analyzer output format to final output schema format."""

    @staticmethod
    def map_to_output_schema(
        feature_data: Dict[str, Any],
        feature_name: str,
        col_position: int,
        col_metadata: Optional[FeatureMetadata] = None,
    ) -> Dict[str, Any]:
        """
        Transform analyzer output to final schema in a single pass.

        Args:
            feature_data: Raw output from analyzer
            feature_name: Name of the feature
            col_position: Position in dataframe
            col_metadata: Optional feature metadata

        Returns:
            Feature data in final output schema format
        """
        # Extract commonly used values once
        stats = feature_data.get("stats", {})
        missing = feature_data.get("missing", {})
        feature_type = feature_data.get("type", "categorical")

        # Build output schema efficiently
        output = {
            "feature_name": feature_name,
            "display_name": feature_data.get("description", ""),
            "description": feature_data.get("description", ""),
            "variable_type": "Continuous" if feature_type == "continuous" else "Categorical",
            "data_type": feature_data.get("data_type", "object"),
            "is_derived": False,
            "is_target": feature_data.get("is_target", False),
        }

        # Add source section
        output["source"] = {
            "type": "provider",
            "provider": feature_data.get("provider"),
        }

        # Add config section
        output["config"] = {
            "default_value": feature_data.get("default_value"),
            "no_hit_value": feature_data.get("no_hit_value"),
        }

        # Build statistics section efficiently
        # Note: stats already contains all analyzer stats including:
        # - count, unique, mode, etc. (categorical)
        # - count, mean, std, min, max, etc. (continuous)
        # - unique_values and unique_ratio (both types)
        # Only add missing-related stats which come from a separate dict
        output["statistics"] = {
            **stats,  # Include all original stats from analyzers
            "missing_count": missing.get("count", 0),
            "missing_percentage": missing.get("percent", 0.0),
        }

        # Add optional sections if present and not None
        if "outliers" in feature_data and feature_data["outliers"] is not None:
            output["outliers"] = feature_data["outliers"]

        if "cardinality" in feature_data and feature_data["cardinality"] is not None:
            output["cardinality"] = feature_data["cardinality"]

        if "distribution" in feature_data and feature_data["distribution"] is not None:
            output["distribution"] = feature_data["distribution"]

        if "target_relationship" in feature_data and feature_data["target_relationship"] is not None:
            output["target_relationship"] = feature_data["target_relationship"]

        if "correlations" in feature_data and feature_data["correlations"] is not None:
            output["correlations"] = feature_data["correlations"]

        if "quality" in feature_data and feature_data["quality"] is not None:
            output["quality"] = feature_data["quality"]

        # Add metadata section
        # output["metadata"] = {
        #     "position": col_position,
        #     "added_at": datetime.now().isoformat() + "Z",
        #     "added_by": "system",
        #     "version": "1.0",
        # }

        return output
