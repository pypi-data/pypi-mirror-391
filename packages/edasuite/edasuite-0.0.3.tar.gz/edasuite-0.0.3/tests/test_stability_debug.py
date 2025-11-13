"""Test to diagnose why some features have null stability."""

import pandas as pd
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from edasuite import EDARunner, DataLoader

def test_stability_null_issue():
    """Diagnose why some features have null stability values."""

    base_path = Path(__file__).parent.parent / 'tmp'

    # Load small sample
    print("Loading dataset sample...")
    df = pd.read_csv(base_path / 'dataset.csv', nrows=1000)

    # Features to track
    test_features = [
        'Original Circle',
        'Original Circle_woe',
        'Active Since',
        'Active Since_woe',
        'Name Match Prediction'
    ]

    print(f"\nTest features exist in dataset:")
    for feat in test_features:
        print(f"  {feat}: {feat in df.columns}")

    # Create a minimal runner with debugging
    print("\n" + "="*80)
    print("Running EDA with stability...")
    print("="*80)

    runner = EDARunner(
        calculate_stability=True,
        cohort_column='dataTag',
        baseline_cohort='training',
        comparison_cohort='test',
        max_correlation_features=20
    )

    results = runner.run(
        data=str(base_path / 'dataset.csv'),
        feature_metadata=str(base_path / 'feature_config.json'),
        target_variable='target_variable',
        output_path=str(base_path / 'debug_stability.json')
    )

    # Analyze results
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)

    # Save and reload to check raw stability data
    with open(base_path / 'debug_stability.json') as f:
        raw_output = json.load(f)

    # The stability results are NOT in the output for cohort-based
    # We need to check the internal state
    print(f"\nTop-level keys in output: {list(raw_output.keys())}")

    # Check what's in top_features_by_statistical_score
    top_features = results.get('top_features_by_statistical_score', [])
    print(f"\nTest features in top_features_by_statistical_score:")
    for test_feat in test_features:
        found = next((f for f in top_features if f['feature_name'] == test_feat), None)
        if found:
            stability = found.get('stability')
            print(f"  {test_feat:40} stability={stability}")
        else:
            print(f"  {test_feat:40} NOT IN TOP FEATURES")

    # Check all features dict
    all_features = results.get('features', [])
    print(f"\nTotal features in output: {len(all_features)}")

    feature_names_in_output = [f['feature_name'] for f in all_features]
    print("\nTest features in features list:")
    for feat in test_features:
        in_output = feat in feature_names_in_output
        print(f"  {feat:40} in output: {in_output}")

if __name__ == '__main__':
    test_stability_null_issue()
