"""JSON output formatter for EDA results."""

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize data structure for JSON serialization.
    Converts NaN, Infinity, and -Infinity to None (null in JSON).

    Args:
        obj: Object to sanitize

    Returns:
        Sanitized object safe for JSON serialization
    """
    import numpy as np

    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj


def safe_round(value: Any, decimals: int = 4) -> Optional[float]:
    """
    Safely round a numeric value, returning None for NaN or Infinity.

    Args:
        value: Value to round
        decimals: Number of decimal places

    Returns:
        Rounded value or None if value is NaN/Infinity
    """
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            if math.isnan(value) or math.isinf(value):
                return None
            return round(float(value), decimals)
        return value
    except (ValueError, TypeError):
        return None


class SafeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that converts NaN and Infinity to null."""

    def default(self, obj):
        """Handle objects that can't be serialized."""
        if isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
        return super().default(obj)

    def encode(self, obj):
        """Encode object after sanitizing."""
        # Sanitize the entire object tree first
        sanitized = sanitize_for_json(obj)
        return super().encode(sanitized)

    def iterencode(self, obj, _one_shot=False):
        """Iterate over encoded chunks after sanitizing."""
        # Sanitize the entire object tree first
        sanitized = sanitize_for_json(obj)
        return super().iterencode(sanitized, _one_shot)


class JSONFormatter:
    """Formats EDA results for JSON output."""

    @staticmethod
    def format_results(
        dataset_info: Dict[str, Any],
        features: Dict[str, Any],
        stability_results: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        execution_time: float = 0.0,
        provider_match_rates: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format EDA results into structured JSON with 3 main sections:
        - metadata: execution metadata and configuration
        - summary: all aggregate statistics and metrics
        - features: individual feature-level analysis

        Args:
            dataset_info: Basic dataset information
            features: Feature analysis results
            correlations: Correlation analysis results (deprecated - embedded in features)
            stability_results: Stability analysis results (PSI/CSI)
            metadata: Additional metadata
            execution_time: Total execution time
            provider_match_rates: Provider match rate statistics

        Returns:
            Formatted dictionary ready for JSON serialization
        """
        # Convert features dict to list and add feature_name
        features_list = []
        for name, data in features.items():
            # Remove metadata subsection from individual features
            feature_data = data.copy()
            if 'metadata' in feature_data:
                del feature_data['metadata']

            feature_data['feature_name'] = name

            # Merge stability data into feature if available
            if stability_results:
                stability_data = {}

                # Add cohort-based stability if available (only key fields)
                if 'feature_stability' in stability_results:
                    cohort_stability = stability_results['feature_stability'].get(name)
                    if cohort_stability:
                        stability_data['cohort_based'] = {
                            'psi': cohort_stability.get('psi'),
                            'stability': cohort_stability.get('stability'),
                            'interpretation': cohort_stability.get('interpretation')
                        }

                # Add time-based stability if available (only key fields)
                if 'time_based_analysis' in stability_results:
                    time_analysis = stability_results['time_based_analysis']
                    if 'feature_stability' in time_analysis:
                        time_stability = time_analysis['feature_stability'].get(name)
                        if time_stability:
                            stability_data['time_based'] = {
                                'avg_psi': time_stability.get('avg_psi'),
                                'max_psi': time_stability.get('max_psi'),
                                'min_psi': time_stability.get('min_psi'),
                                'stability': time_stability.get('stability'),
                                'trend': time_stability.get('trend')
                            }

                # If we have any stability data, add it to the feature
                if stability_data:
                    feature_data['stability'] = stability_data

            features_list.append(feature_data)

        # Compute summary metrics (derived insights only)
        summary_stats = JSONFormatter._compute_summary(features_list, metadata)

        # Compute highest metrics (with stability if available)
        highest_metrics = JSONFormatter._compute_highest_metrics(features_list, stability_results)

        # Compute top 10 features by statistical score
        top_features_by_score = JSONFormatter._compute_top_features_by_statistical_score(features_list, stability_results)

        # Compute data quality summary
        data_quality = JSONFormatter._compute_data_quality(dataset_info, features_list)

        # Compute feature counts for dashboard
        feature_counts = JSONFormatter._compute_feature_counts(features_list, stability_results)

        # Build metadata section with execution info
        metadata_section = {
            "timestamp": datetime.now().isoformat() + "Z",
            "execution_time_seconds": round(execution_time, 2),
            "version": "0.1.0"
        }
        if metadata:
            metadata_section.update(metadata)

        # Build summary section with structured subsections
        summary_section = {
            **summary_stats,  # Derived insights (total_features, avg_missing_percentage, etc.)
            "feature_counts": feature_counts,
            "highest_metrics": highest_metrics,
            "top_features_by_statistical_score": top_features_by_score,
            "data_quality": data_quality,
            "dataset_info": dataset_info  # Raw dataset statistics (single source of truth)
        }

        # Add provider_match_rates to summary if available
        if provider_match_rates:
            summary_section["provider_match_rates"] = provider_match_rates

        # Add stability analysis to summary if available
        if stability_results and stability_results.get('method') == 'time_based':
            summary_section["stability_analysis"] = stability_results

        # Build output with only 3 sections
        output = {
            "metadata": metadata_section,
            "summary": summary_section,
            "features": features_list
        }

        # Sanitize all data to ensure valid JSON
        return sanitize_for_json(output)

    @staticmethod
    def save_json(
        data: Dict[str, Any],
        filepath: Union[str, Path],
        indent: int = 2,
        compact: bool = False
    ) -> None:
        """
        Save formatted data to JSON file.

        Args:
            data: Data to save
            filepath: Output file path
            indent: JSON indentation (None for compact)
            compact: If True, minimize JSON size
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            if compact:
                json.dump(data, f, separators=(',', ':'), cls=SafeJSONEncoder)
            else:
                json.dump(data, f, indent=indent, cls=SafeJSONEncoder)

    @staticmethod
    def to_json_string(
        data: Dict[str, Any],
        indent: Optional[int] = 2,
        compact: bool = False
    ) -> str:
        """
        Convert data to JSON string.

        Args:
            data: Data to convert
            indent: JSON indentation
            compact: If True, minimize JSON size

        Returns:
            JSON string
        """
        if compact:
            return json.dumps(data, separators=(',', ':'), cls=SafeJSONEncoder)
        else:
            return json.dumps(data, indent=indent, cls=SafeJSONEncoder)

    @staticmethod
    def compress_features(features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress feature data for efficient storage.
        
        Removes redundant information and optimizes structure.
        
        Args:
            features: Feature analysis results
            
        Returns:
            Compressed feature data
        """
        compressed = {}

        for name, data in features.items():
            if data.get('type') == 'continuous':
                compressed[name] = {
                    't': 'c',  # type: continuous
                    'm': data.get('missing', {}),  # missing
                    's': {  # stats (abbreviated keys)
                        'mean': data['stats'].get('mean'),
                        'std': data['stats'].get('std'),
                        'min': data['stats'].get('min'),
                        'max': data['stats'].get('max'),
                        'med': data['stats'].get('median')
                    },
                    'o': data.get('outliers', {}).get('count', 0)  # outlier count
                }
            elif data.get('type') == 'categorical':
                compressed[name] = {
                    't': 'cat',  # type: categorical
                    'm': data.get('missing', {}),  # missing
                    'u': data['stats'].get('unique'),  # unique values
                    'mode': data['stats'].get('mode'),
                    'top5': dict(list(data['distribution']['value_counts'].items())[:5])
                }

        return compressed

    @staticmethod
    def _compute_summary(features: list, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compute summary metrics - DERIVED INSIGHTS ONLY.

        Raw dataset statistics are in dataset_info subsection.
        Feature counts are in feature_counts subsection.
        Execution metadata is in metadata section.

        Args:
            features: List of analyzed features
            metadata: Optional metadata dictionary

        Returns:
            Dictionary with derived summary metrics
        """
        total_features = len(features)

        # Count feature types
        feature_type_counts = metadata.get('feature_types', {}) if metadata else {}

        # Calculate averages across features (derived insights)
        missing_percentages = [f.get('statistics', {}).get('missing_percentage', 0) for f in features]
        outlier_percentages = [f.get('outliers', {}).get('percent', 0) for f in features if f.get('outliers')]

        avg_missing = sum(missing_percentages) / len(missing_percentages) if missing_percentages else 0
        avg_outliers = sum(outlier_percentages) / len(outlier_percentages) if outlier_percentages else 0

        # Count provider features (derived from feature metadata)
        provider_features = sum(1 for f in features if f.get('source', {}).get('provider'))
        derived_features = sum(1 for f in features if f.get('is_derived', False))

        return {
            "total_features": total_features,
            "feature_types": feature_type_counts,
            "provider_features": provider_features,
            "derived_features": derived_features,
            "avg_missing_percentage": safe_round(avg_missing, 2),
            "avg_outliers_percentage": safe_round(avg_outliers, 2),
        }

    @staticmethod
    def _compute_highest_metrics(features: list, stability_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Find features with highest metrics."""
        highest_metrics = {}

        # Highest correlation with target
        features_with_corr = [
            (f.get('feature_name'), abs(f.get('target_relationship', {}).get('correlation_pearson', 0)))
            for f in features
            if f.get('target_relationship', {}).get('correlation_pearson') is not None
        ]
        if features_with_corr:
            top_corr = max(features_with_corr, key=lambda x: x[1])
            highest_metrics['highest_correlation'] = {
                'feature_name': top_corr[0],
                'value': safe_round(top_corr[1], 4),
                'target': features[0].get('target_relationship', {}).get('target_variable') if features else None
            }

        # Highest IV
        features_with_iv = [
            (f.get('feature_name'), f.get('target_relationship', {}).get('information_value', 0))
            for f in features
            if f.get('target_relationship', {}).get('information_value') is not None
        ]
        if features_with_iv:
            top_iv = max(features_with_iv, key=lambda x: x[1])
            highest_metrics['highest_iv'] = {
                'feature_name': top_iv[0],
                'value': safe_round(top_iv[1], 4)
            }

        # Highest statistical score (composite score from top_features_by_statistical_score)
        # Use the composite score we calculate: 0.5 * corr + 0.5 * IV
        features_with_statistical_score = []
        for f in features:
            target_rel = f.get('target_relationship', {})
            corr = abs(target_rel.get('correlation_pearson', 0)) if target_rel.get('correlation_pearson') is not None else 0
            iv = target_rel.get('information_value', 0) if target_rel.get('information_value') is not None else 0
            statistical_score = 0.5 * corr + 0.5 * min(iv, 1.0)  # Cap IV at 1 for scoring
            if statistical_score > 0:
                features_with_statistical_score.append((f.get('feature_name'), statistical_score))

        if features_with_statistical_score:
            top_statistical_score = max(features_with_statistical_score, key=lambda x: x[1])
            highest_metrics['highest_statistical_score'] = {
                'feature_name': top_statistical_score[0],
                'value': safe_round(top_statistical_score[1], 4)
            }

        # Highest stability (use PSI from stability_results if available)
        if stability_results and 'feature_stability' in stability_results:
            # Find feature with lowest PSI (most stable)
            stable_features = [
                (fname, data.get('psi'))
                for fname, data in stability_results['feature_stability'].items()
                if data.get('psi') is not None and data.get('stability') == 'stable'
            ]

            if stable_features:
                # Get the most stable (lowest PSI)
                top_stable = min(stable_features, key=lambda x: x[1])
                highest_metrics['highest_stability'] = {
                    'feature_name': top_stable[0],
                    'value': safe_round(top_stable[1], 4),
                    'stability': 'stable',
                    'interpretation': 'Most stable feature (lowest PSI)'
                }
            else:
                highest_metrics['highest_stability'] = {
                    'feature_name': None,
                    'value': None,
                    'note': 'No stable features found (all PSI >= 0.1)'
                }
        else:
            # Placeholder when stability not calculated
            highest_metrics['highest_stability'] = {
                'feature_name': None,
                'value': None,
                'note': 'Stability metrics require cohort data (e.g., train/test split)'
            }

        return highest_metrics

    @staticmethod
    def _compute_top_features_by_statistical_score(features: list, stability_results: Optional[Dict] = None, top_n: int = 10) -> list:
        """Compute top N features based on statistical score (composite of target correlation and IV)."""
        # Extract stability scores by feature name if available
        stability_scores = {}
        if stability_results and 'feature_stability' in stability_results:
            for fname, data in stability_results['feature_stability'].items():
                psi = data.get('psi')
                if psi is not None:
                    # Convert PSI to stability score (lower PSI = higher stability)
                    # PSI < 0.1 = stable (score ~0.9+), 0.1-0.2 = minor shift (score ~0.7-0.9), >0.2 = major shift (score <0.7)
                    # Simple mapping: stability_score = max(0, 1 - psi)
                    stability_scores[fname] = max(0.0, 1.0 - psi)

        # Score features by combination of correlation and IV
        scored_features = []
        for f in features:
            target_rel = f.get('target_relationship', {})
            corr = abs(target_rel.get('correlation_pearson', 0)) if target_rel.get('correlation_pearson') is not None else 0
            iv = target_rel.get('information_value', 0) if target_rel.get('information_value') is not None else 0

            # Composite score: weighted average of correlation and IV
            score = 0.5 * corr + 0.5 * min(iv, 1.0)  # Cap IV at 1 for scoring

            feature_name = f.get('feature_name')
            scored_features.append({
                'feature_name': feature_name,
                'score': score,
                'correlation': safe_round(corr, 4),
                'iv': safe_round(iv, 4),
                'stability': stability_scores.get(feature_name)
            })

        # Sort by score and take top N
        scored_features.sort(key=lambda x: x['score'], reverse=True)
        top_features = scored_features[:top_n]

        # Add rank
        result = []
        for i, f in enumerate(top_features, 1):
            result.append({
                'rank': i,
                'feature_name': f['feature_name'],
                'statistical_score': f['score'],
                'correlation': f['correlation'],
                'iv': f['iv'],
                'stability': safe_round(f['stability'], 4) if f['stability'] is not None else None
            })

        return result

    @staticmethod
    def _compute_feature_counts(features: list, stability_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compute feature counts for dashboard metrics.

        Returns counts for:
        - High correlation features (>0.1)
        - Redundant features (>0.7)
        - High IV features (>0.1)
        - High stability features (PSI < 0.5)

        Args:
            features: List of feature analysis results
            stability_results: Optional stability analysis results

        Returns:
            Dictionary with counts, thresholds, and descriptions for each category
        """
        # Count high correlation features (correlation with target > 0.1)
        high_correlation_count = 0
        high_correlation_threshold = 0.1

        for f in features:
            target_rel = f.get('target_relationship', {})
            corr = target_rel.get('correlation_pearson')
            if corr is not None and abs(corr) > high_correlation_threshold:
                high_correlation_count += 1

        # Count redundant features (high correlation with other features > 0.7)
        redundant_count = 0
        redundancy_threshold = 0.7

        for f in features:
            correlations = f.get('correlations', {})
            top_correlated = correlations.get('top_correlated_features', [])

            # Check if any correlation exceeds redundancy threshold
            for corr_data in top_correlated:
                if abs(corr_data.get('correlation', 0)) > redundancy_threshold:
                    redundant_count += 1
                    break  # Count each feature only once

        # Count high IV features (IV > 0.1)
        high_iv_count = 0
        high_iv_threshold = 0.1

        for f in features:
            target_rel = f.get('target_relationship', {})
            iv = target_rel.get('information_value')
            if iv is not None and iv > high_iv_threshold:
                high_iv_count += 1

        # Count high stability features (PSI < 0.5, meaning stable)
        high_stability_count = 0
        stability_threshold = 0.5

        if stability_results and 'feature_stability' in stability_results:
            for stability_data in stability_results['feature_stability'].values():
                psi = stability_data.get('psi')
                ks = stability_data.get('ks_statistic')

                # Use PSI if available, otherwise KS
                stability_metric = psi if psi is not None else ks

                if stability_metric is not None and stability_metric < stability_threshold:
                    high_stability_count += 1

        return {
            "high_correlation": {
                "count": high_correlation_count,
                "threshold": high_correlation_threshold,
                "description": f"Features with absolute correlation > {high_correlation_threshold}"
            },
            "redundant_features": {
                "count": redundant_count,
                "threshold": redundancy_threshold,
                "description": f"Features with correlation > {redundancy_threshold} with another feature"
            },
            "high_iv": {
                "count": high_iv_count,
                "threshold": high_iv_threshold,
                "description": f"Features with Information Value > {high_iv_threshold}"
            },
            "high_stability": {
                "count": high_stability_count,
                "threshold": stability_threshold,
                "description": f"Features with PSI/KS < {stability_threshold} (more stable)",
                "note": "Lower PSI/KS values indicate higher stability" if high_stability_count > 0 else "Stability analysis not performed or no stable features found"
            }
        }

    @staticmethod
    def _compute_data_quality(dataset_info: Dict[str, Any], features: list) -> Dict[str, Any]:
        """Compute data quality summary."""
        # Find features with quality issues
        features_with_high_missing = [
            f.get('feature_name') for f in features
            if f.get('quality', {}).get('has_high_missing', False)
        ]

        features_with_low_variance = [
            f.get('feature_name') for f in features
            if f.get('quality', {}).get('has_low_variance', False)
        ]

        features_with_outliers = [
            f.get('feature_name') for f in features
            if f.get('quality', {}).get('has_outliers', False)
        ]

        # Calculate overall quality score (0-10)
        # Based on: missing data, duplicates, low variance features, outliers
        total_features = len(features)
        score = 10.0

        # Penalize for high missing
        if features_with_high_missing:
            score -= min(2.0, len(features_with_high_missing) / total_features * 5)

        # Penalize for low variance
        if features_with_low_variance:
            score -= min(1.5, len(features_with_low_variance) / total_features * 3)

        # Penalize for duplicates
        duplicate_rows = dataset_info.get('duplicate_rows', 0)
        total_rows = dataset_info.get('rows', 1)
        if duplicate_rows > 0:
            score -= min(2.0, duplicate_rows / total_rows * 5)

        # Penalize for too many outliers
        outlier_ratio = len(features_with_outliers) / total_features if total_features > 0 else 0
        if outlier_ratio > 0.5:
            score -= 1.5

        score = max(0.0, score)  # Cap at 0

        # Generate recommendations
        recommendations = []
        if features_with_high_missing:
            recommendations.append(f"Consider imputation for {len(features_with_high_missing)} features with >30% missing values")
        if features_with_outliers:
            recommendations.append(f"Review outliers in {len(features_with_outliers)} features")
        if features_with_low_variance:
            recommendations.append(f"Consider removing {len(features_with_low_variance)} low-variance features")
        if duplicate_rows > 0:
            recommendations.append(f"Remove {duplicate_rows} duplicate rows")

        return {
            "overall_score": safe_round(score, 1),
            "total_missing_cells": dataset_info.get('missing_cells', 0),
            "features_with_high_missing_count": len(features_with_high_missing),
            "features_with_low_variance_count": len(features_with_low_variance),
            "features_with_outliers_count": len(features_with_outliers),
            "duplicate_rows": dataset_info.get('duplicate_rows', 0),
            "recommended_actions": recommendations
        }
