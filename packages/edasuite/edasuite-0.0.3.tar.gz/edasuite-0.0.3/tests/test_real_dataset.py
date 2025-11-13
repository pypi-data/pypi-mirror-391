"""Test with real dataset sample."""

import pandas as pd
from pathlib import Path
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from edasuite import EDARunner, DataLoader


def test_real_dataset_sample():
    """Test EDA with real dataset sample."""
    base_path = Path(__file__).parent.parent / 'tmp'

    print("Testing with real dataset sample...")
    print(f"Dataset path: {base_path / 'dataset.csv'}")
    print(f"Feature metadata: {base_path / 'feature_config.json'}")

    # Load sample (first 10k rows to speed up testing)
    print("\nLoading dataset sample (10,000 rows)...")
    df_full = pd.read_csv(base_path / 'dataset.csv', nrows=10000)

    print(f"Dataset shape: {df_full.shape}")
    print(f"Columns: {df_full.columns[:10].tolist()}...")

    # Assume 'target_variable' is the target - check if it exists
    if 'target_variable' not in df_full.columns:
        # Find a suitable target column (usually something with 'target', 'label', or binary values)
        potential_targets = [col for col in df_full.columns if 'target' in col.lower() or 'label' in col.lower()]
        if potential_targets:
            target = potential_targets[0]
            print(f"\nUsing target column: {target}")
        else:
            # Use last column as target
            target = df_full.columns[-1]
            print(f"\nUsing last column as target: {target}")
    else:
        target = 'target_variable'
        print(f"\nUsing target column: {target}")

    # Save sample
    sample_csv = base_path / 'dataset_sample_10k.csv'
    df_full.to_csv(sample_csv, index=False)
    print(f"Saved sample to: {sample_csv}")

    # Run EDA with feature metadata
    print("\nRunning EDA with feature metadata...")
    start_time = time.time()

    runner = EDARunner(
        max_correlation_features=100  # Limit correlation matrix for speed
    )

    results = runner.run(
        data=sample_csv,
        feature_metadata=base_path / 'feature_config.json',
        target_variable=target,
        output_path=base_path / 'real_dataset_eda_enhanced.json'
    )

    elapsed = time.time() - start_time

    # Print results
    print(f"\n✅ EDA completed in {elapsed:.2f} seconds")
    print("\n" + "="*80)
    print("SUMMARY METRICS")
    print("="*80)

    summary = results['summary']
    print(f"Total Features: {summary['total_features']}")
    print(f"Total Rows: {summary['total_rows']}")
    print(f"Provider Features: {summary['provider_features']}")
    print(f"Memory Usage: {summary['memory_usage_mb']:.2f} MB")
    print(f"Avg Missing %: {summary['avg_missing_percentage']}")
    print(f"Avg Outliers %: {summary['avg_outliers_percentage']}")
    print(f"\nFeature Type Breakdown:")
    for ftype, count in summary['feature_types'].items():
        print(f"  {ftype}: {count}")

    print(f"\nQuality Metrics:")
    print(f"  High Correlation Features: {summary['high_correlation_features']}")
    print(f"  Redundant Features: {summary['redundant_features']}")
    print(f"  High IV Features: {summary['high_iv_features']}")

    print("\n" + "="*80)
    print("HIGHEST METRICS")
    print("="*80)

    if 'highest_correlation' in results['highest_metrics']:
        hc = results['highest_metrics']['highest_correlation']
        print(f"Highest Correlation: {hc['feature_name']}")
        print(f"  Value: {hc['value']}")
        print(f"  Target: {hc['target']}")

    if 'highest_iv' in results['highest_metrics']:
        hi = results['highest_metrics']['highest_iv']
        print(f"\nHighest Information Value: {hi['feature_name']}")
        print(f"  IV: {hi['value']}")

    if 'highest_statistical_score' in results['highest_metrics']:
        hi = results['highest_metrics']['highest_statistical_score']
        print(f"\nHighest Statistical Score: {hi['feature_name']}")
        print(f"  Score: {hi['value']}")

    if 'highest_stability' in results['highest_metrics']:
        hs = results['highest_metrics']['highest_stability']
        if hs['feature_name']:
            print(f"\nHighest Stability: {hs['feature_name']}")
            print(f"  Score: {hs['value']}")
        else:
            print(f"\nHighest Stability: {hs.get('note', 'Not available')}")

    print("\n" + "="*80)
    print("TOP 10 FEATURES BY STATISTICAL SCORE")
    print("="*80)

    for feat in results['top_features_by_statistical_score'][:10]:
        print(f"{feat['rank']:2d}. {feat['feature_name']:40s} "
              f"score={feat['statistical_score']:7.4f}  corr={feat['correlation']:7.4f}  iv={feat['iv']:7.4f}")

    print("\n" + "="*80)
    print("DATA QUALITY")
    print("="*80)

    dq = results['data_quality']
    print(f"Overall Score: {dq['overall_score']}/10")
    print(f"Features with high missing: {len(dq['features_with_high_missing'])}")
    print(f"Features with low variance: {len(dq['features_with_low_variance'])}")
    print(f"Features with outliers: {len(dq['features_with_outliers'])}")
    print(f"\nRecommendations ({len(dq['recommended_actions'])}):")
    for i, rec in enumerate(dq['recommended_actions'][:5], 1):
        print(f"  {i}. {rec}")
    if len(dq['recommended_actions']) > 5:
        print(f"  ... and {len(dq['recommended_actions']) - 5} more")

    print("\n" + "="*80)
    print("SAMPLE FEATURE DETAILS")
    print("="*80)

    # Show details of top feature
    if results['features']:
        top_feat = results['features'][0]
        print(f"\nFeature: {top_feat['feature_name']}")
        print(f"  Variable Type: {top_feat['variable_type']}")
        print(f"  Provider: {top_feat.get('source', {}).get('provider', 'N/A')}")
        print(f"  Description: {top_feat.get('description', 'N/A')[:80]}...")

        if 'statistics' in top_feat:
            stats = top_feat['statistics']
            print(f"\n  Statistics:")
            if 'mean' in stats:
                print(f"    Mean: {stats.get('mean')}")
                print(f"    Std: {stats.get('std')}")
                print(f"    Min/Max: {stats.get('min')} / {stats.get('max')}")
            if 'unique' in stats:
                print(f"    Unique Values: {stats.get('unique')}")
                print(f"    Mode: {stats.get('mode')}")

        if 'target_relationship' in top_feat:
            tr = top_feat['target_relationship']
            print(f"\n  Target Relationship:")
            print(f"    Pearson Corr: {tr.get('correlation_pearson')}")
            print(f"    Spearman Corr: {tr.get('correlation_spearman')}")
            print(f"    Information Value: {tr.get('information_value')}")
            print(f"    Predictive Power: {tr.get('predictive_power')}")

        if 'quality' in top_feat:
            quality = top_feat['quality']
            print(f"\n  Quality Flags:")
            print(f"    High Missing: {quality.get('has_high_missing')}")
            print(f"    Low Variance: {quality.get('has_low_variance')}")
            print(f"    Has Outliers: {quality.get('has_outliers')}")
            print(f"    Recommended for Modeling: {quality.get('recommended_for_modeling')}")

    print("\n" + "="*80)
    print(f"\n✅ Full output saved to: {base_path / 'real_dataset_eda_enhanced.json'}")
    print(f"File size: {(base_path / 'real_dataset_eda_enhanced.json').stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    test_real_dataset_sample()
