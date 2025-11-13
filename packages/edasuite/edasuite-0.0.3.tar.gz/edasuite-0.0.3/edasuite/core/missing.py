"""Missing value handling utilities."""

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from edasuite.core.logging_config import get_logger

# Setup module logger
logger = get_logger(__name__)


def replace_sentinel_values_with_nulls(
    df: pd.DataFrame,
    feature_metadata: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Replace sentinel values (default_value, no_hit_value) with proper nulls.

    This function treats special marker values defined in feature metadata
    as missing data and replaces them with np.nan. This improves data quality
    analysis and ensures proper missing value handling throughout the pipeline.

    Args:
        df: Input DataFrame
        feature_metadata: Dictionary mapping feature names to FeatureMetadata objects.
                         Expected structure:
                         {
                             "feature_name": FeatureMetadata(
                                 name="feature_name",
                                 default=-1,
                                 no_hit_value="-1",
                                 ...
                             ),
                             ...
                         }

    Returns:
        DataFrame with sentinel values replaced by np.nan

    Example:
        >>> from edasuite.core.types import FeatureMetadata
        >>> metadata = {
        ...     "age": FeatureMetadata(name="age", no_hit_value="-1"),
        ...     "name": FeatureMetadata(name="name", no_hit_value="")
        ... }
        >>> df = pd.DataFrame({"age": [25, -1, 30], "name": ["Alice", "", "Bob"]})
        >>> df_clean = replace_sentinel_values_with_nulls(df, metadata)
        >>> df_clean.isna().sum()
        age     1
        name    1
        dtype: int64
    """
    if feature_metadata is None or not feature_metadata:
        return df.copy()

    # Create a copy to avoid modifying the original
    df_clean = df.copy()

    replacement_count = 0
    features_processed = []

    # Iterate over the metadata dictionary
    for feature_name, metadata_obj in feature_metadata.items():
        if not feature_name or feature_name not in df_clean.columns:
            continue

        sentinel_values = []

        # Collect all sentinel values for this feature
        default_value = metadata_obj.default
        no_hit_value = metadata_obj.no_hit_value

        if default_value is not None:
            sentinel_values.append(default_value)

        if no_hit_value is not None:
            sentinel_values.append(no_hit_value)

        # Replace sentinel values with null
        feature_replaced = False

        # Skip if no sentinel values configured
        if not sentinel_values:
            continue

        # Handle configured sentinels
        for sentinel in sentinel_values:
            # Handle type conversion for comparison
            try:
                # For numeric columns, try to convert sentinel to numeric
                if pd.api.types.is_numeric_dtype(df_clean[feature_name]):
                    if isinstance(sentinel, str):
                        # Try to parse string sentinel as number
                        try:
                            sentinel_numeric = float(sentinel)
                            mask = df_clean[feature_name] == sentinel_numeric
                        except (ValueError, TypeError):
                            # If can't convert, compare as string
                            mask = df_clean[feature_name].astype(str) == sentinel
                    else:
                        mask = df_clean[feature_name] == sentinel
                else:
                    # For string columns, compare as strings
                    # Handle empty string sentinel
                    if sentinel == '':
                        # Only match actual empty strings, not existing nulls
                        mask = (df_clean[feature_name] == '') & df_clean[feature_name].notna()
                    else:
                        # Convert to string for comparison
                        mask = df_clean[feature_name].astype(str) == str(sentinel)

                # Apply replacement
                if mask.any():
                    count_before = df_clean[feature_name].isna().sum()
                    df_clean.loc[mask, feature_name] = np.nan
                    count_after = df_clean[feature_name].isna().sum()
                    replaced = count_after - count_before

                    if replaced > 0:
                        replacement_count += replaced
                        feature_replaced = True

            except Exception as e:
                # Log warning but continue processing
                logger.warning(f"  Warning: Could not replace sentinel '{sentinel}' in feature '{feature_name}': {e}")
                continue

        if feature_replaced:
            features_processed.append(feature_name)

    if replacement_count > 0:
        logger.info(f"\nReplaced {replacement_count:,} sentinel values with nulls across {len(features_processed)} features")

    return df_clean


def compute_provider_match_rates(
    df: pd.DataFrame,
    feature_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Compute match rates (hit rates) by provider.

    Provider match rate indicates what percentage of records have
    valid (non-null, non-sentinel) values from each data provider.

    This function supports two methods for computing match rates:
    1. Using <provider>_user_not_found columns if available (more accurate)
    2. Falling back to feature-level null analysis from metadata

    Args:
        df: DataFrame with features (after sentinel value replacement)
        feature_metadata: Dictionary mapping feature names to FeatureMetadata objects.
                         Expected structure:
                         {
                             "feature_name": FeatureMetadata(
                                 name="feature_name",
                                 provider="provider_name",
                                 ...
                             ),
                             ...
                         }

    Returns:
        Dictionary mapping provider names to their statistics:
        {
            "provider_name": {
                "match_rate": 0.85,  # Overall match rate (hit rate) - % records where user found
                "hit_rate": 0.85,    # Alias for match_rate
                "total_features": 10,
                "total_records": 1000,
                "matched_records": 850,
                "not_found_records": 150,  # If user_not_found column exists
                "computation_method": "user_not_found_column" or "feature_analysis",
                "feature_match_rate": 0.75  # Overall: % of non-null values across all features
            },
            ...
        }

    Example:
        >>> from edasuite.core.types import FeatureMetadata
        >>> # Method 1: Using user_not_found column
        >>> df = pd.DataFrame({
        ...     "age": [25, None, 30],
        ...     "income": [50000, None, None],
        ...     "bureau_user_not_found": [0, 1, 0]
        ... })
        >>> metadata = {
        ...     "age": FeatureMetadata(name="age", provider="bureau"),
        ...     "income": FeatureMetadata(name="income", provider="bureau")
        ... }
        >>> rates = compute_provider_match_rates(df, metadata)
        >>> rates["bureau"]["hit_rate"]  # 2 out of 3 records found
        0.6667

        >>> # Method 2: Feature-level analysis (fallback)
        >>> df2 = pd.DataFrame({"age": [25, None, 30], "income": [50000, 60000, None]})
        >>> rates2 = compute_provider_match_rates(df2, metadata)
        >>> rates2["bureau"]["match_rate"]
        0.6666666666666666
    """
    if feature_metadata is None or not feature_metadata:
        # Try to detect providers from <provider>_user_not_found columns
        return _compute_provider_match_rates_from_columns(df)

    # Group features by provider
    provider_features = {}
    for feature_name, metadata_obj in feature_metadata.items():
        provider = metadata_obj.provider

        if not provider or not feature_name or feature_name not in df.columns:
            continue

        if provider not in provider_features:
            provider_features[provider] = []

        provider_features[provider].append(feature_name)

    # Compute match rates for each provider
    provider_stats = {}
    total_records = len(df)

    for provider, features in provider_features.items():
        # Check if <provider>_user_not_found column exists
        user_not_found_col = f"{provider}_user_not_found"

        if user_not_found_col in df.columns:
            # Method 1: Use the user_not_found column (more accurate)
            # Assuming: 0 = user found, 1 = user not found, null = unknown/error
            not_found_mask = df[user_not_found_col] == 1
            found_mask = df[user_not_found_col] == 0

            not_found_records = not_found_mask.sum()
            matched_records = found_mask.sum()
            overall_match_rate = matched_records / total_records if total_records > 0 else 0

            # Compute overall feature match rate (% of non-null values across all features)
            total_cells = len(features) * total_records
            non_null_cells = sum(df[feature].notna().sum() for feature in features)
            feature_match_rate = non_null_cells / total_cells if total_cells > 0 else 0

            provider_stats[provider] = {
                "match_rate": round(overall_match_rate, 4),
                "hit_rate": round(overall_match_rate, 4),
                "total_features": len(features),
                "total_records": total_records,
                "matched_records": int(matched_records),
                "not_found_records": int(not_found_records),
                "computation_method": "user_not_found_column",
                "feature_match_rate": round(feature_match_rate, 4)
            }

        else:
            # Method 2: Feature-level analysis (original method)
            provider_matched_per_record = []
            total_cells = len(features) * total_records
            non_null_cells = 0

            for feature in features:
                non_null_count = df[feature].notna().sum()
                non_null_cells += non_null_count

                # Track per-record: 1 if this feature has value, 0 if null
                provider_matched_per_record.append(df[feature].notna())

            # Aggregate: a record "matches" if it has at least one non-null value from this provider
            if provider_matched_per_record:
                any_match_per_record = pd.concat(provider_matched_per_record, axis=1).any(axis=1)
                matched_records = any_match_per_record.sum()
                overall_match_rate = matched_records / total_records if total_records > 0 else 0
            else:
                matched_records = 0
                overall_match_rate = 0.0

            # Compute overall feature match rate (% of non-null values across all features)
            feature_match_rate = non_null_cells / total_cells if total_cells > 0 else 0

            provider_stats[provider] = {
                "match_rate": round(overall_match_rate, 4),
                "hit_rate": round(overall_match_rate, 4),
                "total_features": len(features),
                "total_records": total_records,
                "matched_records": int(matched_records),
                "computation_method": "feature_analysis",
                "feature_match_rate": round(feature_match_rate, 4)
            }

    return provider_stats


def _compute_provider_match_rates_from_columns(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Detect and compute provider match rates from <provider>_user_not_found columns.

    This is a fallback method when no feature metadata is provided.

    Args:
        df: DataFrame potentially containing <provider>_user_not_found columns

    Returns:
        Dictionary mapping provider names to their statistics
    """
    import re

    provider_stats = {}
    total_records = len(df)

    # Find all columns matching pattern <provider>_user_not_found
    user_not_found_pattern = re.compile(r'^(.+)_user_not_found$')

    for col in df.columns:
        match = user_not_found_pattern.match(col)
        if match:
            provider = match.group(1)

            # Compute match rate from user_not_found column
            # Assuming: 0 = user found, 1 = user not found
            not_found_mask = df[col] == 1
            found_mask = df[col] == 0

            not_found_records = not_found_mask.sum()
            matched_records = found_mask.sum()
            overall_match_rate = matched_records / total_records if total_records > 0 else 0

            provider_stats[provider] = {
                "match_rate": round(overall_match_rate, 4),
                "hit_rate": round(overall_match_rate, 4),
                "total_features": 0,  # Unknown without metadata
                "total_records": total_records,
                "matched_records": int(matched_records),
                "not_found_records": int(not_found_records),
                "computation_method": "user_not_found_column",
                "feature_match_rate": 0.0  # Unknown without metadata
            }

    return provider_stats
