"""Main EDA orchestrator."""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from edasuite.analyzers.basic import BasicStatsAnalyzer
from edasuite.analyzers.stability import StabilityAnalyzer
from edasuite.core.correlation import CorrelationEngine
from edasuite.core.feature_processor import FeatureProcessor
from edasuite.core.logging_config import get_logger
from edasuite.core.types import FeatureMetadata
from edasuite.output.formatter import JSONFormatter

# Setup module logger
logger = get_logger(__name__)


class EDARunner:
    """Main orchestrator for EDA pipeline."""

    def __init__(
        self,
        max_categories: int = 50,
        sample_size: Optional[int] = None,
        top_correlations: int = 10,
        max_correlation_features: Optional[int] = None,
        # Cohort-based stability
        calculate_stability: bool = False,
        cohort_column: Optional[str] = None,
        baseline_cohort: Optional[str] = None,
        comparison_cohort: Optional[str] = None,
        # Time-based stability
        time_based_stability: bool = False,
        time_column: Optional[str] = None,
        time_window_strategy: str = 'monthly',
        baseline_period: Union[str, tuple] = 'first',
        comparison_periods: Union[str, List[tuple]] = 'all',
        min_samples_per_period: int = 100
    ):
        """
        Initialize EDA Runner.

        Args:
            max_categories: Maximum categories for categorical analysis
            sample_size: Optional sample size for large datasets
            top_correlations: Number of top correlations to show per feature
            max_correlation_features: Maximum features for correlation matrix. None = no limit

            # Cohort-based stability
            calculate_stability: Whether to calculate cohort-based stability (requires cohort_column)
            cohort_column: Column name for cohort identification (e.g., 'dataTag')
            baseline_cohort: Baseline cohort value (e.g., 'training')
            comparison_cohort: Comparison cohort value (e.g., 'test')

            # Time-based stability
            time_based_stability: Whether to calculate time-based stability (requires time_column)
            time_column: Column name with timestamps (e.g., 'onboarding_time')
            time_window_strategy: 'monthly', 'weekly', 'quartiles', or 'custom'
            baseline_period: 'first' (auto-detect) or tuple ('start_date', 'end_date')
            comparison_periods: 'all' (auto-detect all periods) or list of tuples
            min_samples_per_period: Minimum samples required per time period
        """
        self.max_categories = max_categories
        self.sample_size = sample_size
        self.top_correlations = top_correlations
        self.max_correlation_features = max_correlation_features

        # Cohort-based stability
        self.calculate_stability = calculate_stability
        self.cohort_column = cohort_column
        self.baseline_cohort = baseline_cohort
        self.comparison_cohort = comparison_cohort

        # Time-based stability
        self.time_based_stability = time_based_stability
        self.time_column = time_column
        self.time_window_strategy = time_window_strategy
        self.baseline_period = baseline_period
        self.comparison_periods = comparison_periods
        self.min_samples_per_period = min_samples_per_period

        # Initialize analyzers and processors
        self.basic_analyzer = BasicStatsAnalyzer()
        self.stability_analyzer = StabilityAnalyzer()
        self.correlation_engine = CorrelationEngine(top_correlations, max_correlation_features)
        self.feature_processor = FeatureProcessor(max_categories, self.correlation_engine)

        # JSON formatter
        self.formatter = JSONFormatter()

    def run(
        self,
        data: pd.DataFrame,
        feature_metadata: Optional[Dict[str, FeatureMetadata]] = None,
        output_path: Optional[Union[str, Path]] = None,
        compact_json: bool = False,
        columns: Optional[List[str]] = None,
        target_variable: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run complete EDA pipeline.

        Args:
            data: DataFrame to analyze
            feature_metadata: Optional dict mapping feature names to FeatureMetadata objects
            output_path: Optional path to save JSON output
            compact_json: If True, minimize JSON size
            columns: Optional list of columns to analyze (overrides feature_metadata)
            target_variable: Name of target variable column

        Returns:
            Complete EDA results as dictionary
        """
        start_time = time.perf_counter()

        # Use provided DataFrame
        logger.info("Running EDA analysis...")
        df = data
        if self.sample_size and len(df) > self.sample_size:
            logger.info(f"Sampling {self.sample_size} rows from {len(df)} total rows")
            df = df.head(self.sample_size)

        # Use provided feature metadata
        feature_metadata_dict = feature_metadata or {}


        if feature_metadata_dict and not columns:  # If columns not explicitly provided, use feature metadata
            # Only include features that have a provider set
            columns = [
                name for name, metadata in feature_metadata_dict.items()
                if metadata.provider is not None
            ]
            logger.info(f"Found {len(columns)} features with provider in metadata")
        elif columns:
            logger.info(f"Using explicitly provided columns list with {len(columns)} features")

        # Filter columns if specified (either from metadata or explicit list)
        if columns:
            missing_cols = set(columns) - set(df.columns)
            if missing_cols:
                logger.warning(f" {len(missing_cols)} features not found in dataset")
                logger.info(f"Missing features: {list(missing_cols)[:10]}...")  # Show first 10

            available_cols = [col for col in columns if col in df.columns]

            # Exclude time_column and cohort_column from feature analysis
            if self.cohort_column and self.cohort_column in available_cols:
                available_cols.remove(self.cohort_column)
                logger.info(f"Excluded cohort column from feature analysis: {self.cohort_column}")

            if self.time_column and self.time_column in available_cols:
                available_cols.remove(self.time_column)
                logger.info(f"Excluded time column from feature analysis: {self.time_column}")

            logger.info(f"Analyzing {len(available_cols)} available features")

            # Include target variable if specified and not already included
            if target_variable and target_variable in df.columns and target_variable not in available_cols:
                available_cols.append(target_variable)
                logger.info(f"Added target variable: {target_variable}")

            # Build list of columns to keep in dataframe (features + metadata columns)
            df_columns = available_cols.copy()

            # Include cohort column for cohort-based stability calculation if needed
            if (
                self.calculate_stability
                and self.cohort_column
                and self.cohort_column in df.columns
                and self.cohort_column not in df_columns
            ):
                df_columns.append(self.cohort_column)
                logger.info(f"Keeping cohort column for stability calculation: {self.cohort_column}")

            # Include time column for time-based stability calculation if needed
            if (
                self.time_based_stability
                and self.time_column
                and self.time_column in df.columns
                and self.time_column not in df_columns
            ):
                df_columns.append(self.time_column)
                logger.info(f"Keeping time column for stability calculation: {self.time_column}")

            df = df[df_columns]

        # Replace sentinel values with proper nulls
        if feature_metadata_dict:
            from edasuite.core.missing import replace_sentinel_values_with_nulls
            logger.info("\nReplacing sentinel values (no-hit, default) with nulls...")
            df = replace_sentinel_values_with_nulls(df, feature_metadata_dict)

        # Run basic analysis
        logger.info("\nRunning basic dataset analysis...")
        dataset_info = self.basic_analyzer.analyze_dataframe(df, feature_metadata_dict)

        # Calculate correlations for numeric features
        logger.info("Computing feature correlations...")
        correlation_matrix = self.correlation_engine.compute_correlation_matrix(df, target_variable)

        # Analyze each feature (only those in available_cols, excluding metadata columns)
        logger.info(f"Analyzing {len(available_cols) if columns else len(df.columns)} features...")
        features = self.feature_processor.analyze_features(
            df=df,
            feature_metadata_dict=feature_metadata_dict,
            target_variable=target_variable,
            correlation_matrix=correlation_matrix,
            precomputed_correlations=None,  # TODO: Extract from feature_metadata if available
            columns_to_analyze=available_cols if columns else None
        )

        # Calculate stability if requested
        stability_results = None

        # Cohort-based stability
        if self.calculate_stability and self.cohort_column:
            if self.cohort_column in df.columns:
                logger.info(f"\nCalculating cohort-based stability using '{self.cohort_column}'...")

                # Build feature types dict
                # Use the feature type from analysis, or determine using metadata if missing
                feature_types = {}
                for name, data in features.items():
                    ftype = data.get('variable_type')
                    if not ftype:
                        # Fallback: determine using metadata if available
                        from edasuite.core.base import BaseAnalyzer
                        col_metadata = feature_metadata_dict.get(name) if feature_metadata_dict else None
                        inferred = BaseAnalyzer.determine_feature_type(df[name], col_metadata)
                        # For stability, treat datetime/text as categorical, only continuous if actually continuous
                        ftype = 'continuous' if inferred.value == 'continuous' else 'categorical'
                    feature_types[name] = ftype

                # Default cohorts if not specified
                baseline = self.baseline_cohort or 'training'
                comparison = self.comparison_cohort or 'test'

                features_to_analyze = list(features.keys())

                stability_results = self.stability_analyzer.calculate_stability_for_dataset(
                    df=df,
                    cohort_column=self.cohort_column,
                    baseline_cohort=baseline,
                    comparison_cohort=comparison,
                    features_to_analyze=features_to_analyze,
                    feature_types=feature_types
                )
            else:
                logger.warning(f" Cohort column '{self.cohort_column}' not found. Skipping cohort-based stability calculation.")

        # Time-based stability
        if self.time_based_stability and self.time_column:
            if self.time_column in df.columns:
                logger.info(f"\nCalculating time-based stability using '{self.time_column}'...")

                # Build feature types dict
                # Use the feature type from analysis, or determine using metadata if missing
                feature_types = {}
                for name, data in features.items():
                    ftype = data.get('type')
                    if not ftype:
                        # Fallback: determine using metadata if available
                        from edasuite.core.base import BaseAnalyzer
                        col_metadata = feature_metadata_dict.get(name) if feature_metadata_dict else None
                        inferred = BaseAnalyzer.determine_feature_type(df[name], col_metadata)
                        # For stability, treat datetime/text as categorical, only continuous if actually continuous
                        ftype = 'continuous' if inferred.value == 'continuous' else 'categorical'
                    feature_types[name] = ftype

                # Exclude time column and target from stability analysis
                features_to_analyze = [
                    f for f in features
                    if f != self.time_column and f != target_variable
                ]

                time_stability_results = self.stability_analyzer.calculate_stability_time_based(
                    df=df,
                    time_column=self.time_column,
                    baseline_window=self.baseline_period,
                    comparison_windows=self.comparison_periods,
                    features_to_analyze=features_to_analyze,
                    feature_types=feature_types,
                    window_strategy=self.time_window_strategy,
                    min_samples_per_period=self.min_samples_per_period
                )

                # If no cohort-based stability, use time-based as the main results
                # Otherwise, merge both (prioritize time-based for highest_stability)
                if stability_results is None:
                    stability_results = time_stability_results
                else:
                    # Merge both results - add time-based as additional section
                    stability_results['time_based_analysis'] = time_stability_results

            else:
                logger.warning(f" Time column '{self.time_column}' not found. Skipping time-based stability calculation.")

        # Compute provider match rates before formatting
        # Try with metadata first, then auto-detect from user_not_found columns
        from edasuite.core.missing import compute_provider_match_rates
        logger.info("\nComputing provider match rates...")
        provider_stats = compute_provider_match_rates(df, feature_metadata_dict)
        if provider_stats:
            logger.info(f"  Computed match rates for {len(provider_stats)} providers")
        else:
            logger.info("  No provider match rates computed (no metadata or user_not_found columns found)")

        # Format results
        execution_time = time.perf_counter() - start_time
        results = self.formatter.format_results(
            dataset_info=dataset_info['dataset_info'],
            stability_results=stability_results,
            provider_match_rates=provider_stats,  # Pass provider stats to formatter
            features=features,
            metadata={
                "target_variable": target_variable,
                "max_categories": self.max_categories,
                "sample_size": self.sample_size,
                "top_correlations": self.top_correlations,
                "max_correlation_features": self.max_correlation_features,
                "feature_metadata_available": bool(feature_metadata_dict),
                "feature_types": dataset_info.get('feature_types', {}),  # Pass feature type counts
                "correlation_config": {
                    "top_correlations": self.top_correlations,
                    "correlation_threshold": 0.1
                },
                # Add stability configs only if enabled, separately for cohort and time based
                **({
                    "cohort_stability_config": {
                        "cohort_column": self.cohort_column,
                        "baseline_cohort": self.baseline_cohort,
                        "comparison_cohort": self.comparison_cohort
                    }
                } if self.calculate_stability else {}),
                **({
                    "time_stability_config": {
                        "time_window_strategy": self.time_window_strategy,
                        "baseline_period": self.baseline_period,
                        "comparison_periods": self.comparison_periods,
                        "min_samples_per_period": self.min_samples_per_period,
                        "time_column": self.time_column
                    }
                } if self.time_based_stability else {}),
            },
            execution_time=execution_time
        )

        # Save if output path provided
        if output_path:
            logger.info(f"Saving results to {output_path}...")
            self.formatter.save_json(results, output_path, compact=compact_json)

        logger.info(f"EDA completed in {execution_time:.2f} seconds")
        return results
