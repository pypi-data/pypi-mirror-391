"""Test new EDA schema implementation."""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from edasuite import EDARunner, DataLoader


def create_test_dataset():
    """Create a small test dataset with target variable."""
    np.random.seed(42)
    n_samples = 1000

    df = pd.DataFrame({
        'feature_continuous_1': np.random.normal(100, 15, n_samples),
        'feature_continuous_2': np.random.uniform(0, 1, n_samples),
        'feature_categorical_1': np.random.choice(['A', 'B', 'C', 'D'], n_samples),
        'feature_categorical_2': np.random.choice(['Low', 'Medium', 'High'], n_samples),
        'target': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    })

    # Add some missing values
    df.loc[np.random.choice(df.index, 50), 'feature_continuous_1'] = np.nan
    df.loc[np.random.choice(df.index, 30), 'feature_categorical_1'] = np.nan

    # Add some outliers
    df.loc[np.random.choice(df.index, 20), 'feature_continuous_1'] = 500

    return df


def test_new_schema():
    """Test EDA with new schema."""
    print("Creating test dataset...")
    df = create_test_dataset()

    # Save to CSV
    test_csv = Path(__file__).parent.parent / 'tmp' / 'test_new_schema.csv'
    test_csv.parent.mkdir(exist_ok=True, parents=True)
    df.to_csv(test_csv, index=False)

    print(f"Saved test dataset to {test_csv}")
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Run EDA
    print("\nRunning EDA...")
    runner = EDARunner()
    results = runner.run(
        data=test_csv,
        target_variable='target',
        output_path=test_csv.parent / 'test_new_schema_output.json'
    )

    # Verify structure
    print("\nVerifying output structure...")
    assert 'summary' in results, "Missing 'summary' section"
    assert 'highest_metrics' in results, "Missing 'highest_metrics' section"
    assert 'top_features_by_statistical_score' in results, "Missing 'top_features_by_statistical_score' section"
    assert 'data_quality' in results, "Missing 'data_quality' section"
    assert 'features' in results, "Missing 'features' section"
    assert isinstance(results['features'], list), "'features' should be a list"

    # Check summary fields
    summary = results['summary']
    print("\n=== SUMMARY ===")
    print(f"Total Features: {summary.get('total_features')}")
    print(f"Total Rows: {summary.get('total_rows')}")
    print(f"Avg Missing %: {summary.get('avg_missing_percentage')}")
    print(f"Avg Outliers %: {summary.get('avg_outliers_percentage')}")
    print(f"High IV Features: {summary.get('high_iv_features')}")
    print(f"Redundant Features: {summary.get('redundant_features')}")

    assert summary.get('total_features') == 5, "Should have 5 features"
    assert summary.get('total_rows') == 1000, "Should have 1000 rows"

    # Check highest metrics
    print("\n=== HIGHEST METRICS ===")
    if 'highest_correlation' in results['highest_metrics']:
        hc = results['highest_metrics']['highest_correlation']
        print(f"Highest Correlation: {hc['feature_name']} = {hc['value']}")
    if 'highest_iv' in results['highest_metrics']:
        hi = results['highest_metrics']['highest_iv']
        print(f"Highest IV: {hi['feature_name']} = {hi['value']}")
    if 'highest_statistical_score' in results['highest_metrics']:
        hi = results['highest_metrics']['highest_statistical_score']
        print(f"Highest Statistical Score: {hi['feature_name']} = {hi['value']}")
    if 'highest_stability' in results['highest_metrics']:
        hs = results['highest_metrics']['highest_stability']
        if hs['feature_name']:
            print(f"Highest Stability: {hs['feature_name']} = {hs['value']}")
        else:
            print(f"Highest Stability: Not available ({hs.get('note', 'N/A')})")

    # Check top features by statistical score
    print("\n=== TOP FEATURES BY STATISTICAL SCORE ===")
    for feat in results['top_features_by_statistical_score'][:5]:
        print(f"{feat['rank']}. {feat['feature_name']}: "
              f"score={feat['statistical_score']}, corr={feat['correlation']}, iv={feat['iv']}")

    # Check data quality
    print("\n=== DATA QUALITY ===")
    dq = results['data_quality']
    print(f"Overall Score: {dq['overall_score']}/10")
    print(f"Features with high missing: {len(dq['features_with_high_missing'])}")
    print(f"Features with outliers: {len(dq['features_with_outliers'])}")
    print(f"Recommendations: {len(dq['recommended_actions'])}")
    for rec in dq['recommended_actions']:
        print(f"  - {rec}")

    # Check feature structure
    print("\n=== FEATURE STRUCTURE ===")
    if results['features']:
        feat = results['features'][0]
        print(f"Feature: {feat.get('feature_name')}")
        print(f"  Variable Type: {feat.get('variable_type')}")
        print(f"  Has 'source': {('source' in feat)}")
        print(f"  Has 'config': {('config' in feat)}")
        print(f"  Has 'statistics': {('statistics' in feat)}")
        print(f"  Has 'target_relationship': {('target_relationship' in feat)}")
        print(f"  Has 'correlations': {('correlations' in feat)}")
        print(f"  Has 'quality': {('quality' in feat)}")
        print(f"  Has 'metadata': {('metadata' in feat)}")

        # Check target_relationship for IV and WoE
        if 'target_relationship' in feat:
            tr = feat['target_relationship']
            print(f"\n  Target Relationship:")
            print(f"    - Pearson Correlation: {tr.get('correlation_pearson')}")
            print(f"    - Spearman Correlation: {tr.get('correlation_spearman')}")
            print(f"    - Information Value: {tr.get('information_value')}")
            print(f"    - Predictive Power: {tr.get('predictive_power')}")
            if tr.get('woe_mapping'):
                print(f"    - WoE Mapping: {list(tr['woe_mapping'].keys())[:5]}")

    print("\n✅ All tests passed!")
    print(f"\nOutput saved to: {test_csv.parent / 'test_new_schema_output.json'}")


if __name__ == '__main__':
    test_new_schema()
