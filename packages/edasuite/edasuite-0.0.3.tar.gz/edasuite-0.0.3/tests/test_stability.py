"""Test stability calculation with real dataset."""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from edasuite import EDARunner, DataLoader


def test_stability():
    """Test stability with train/test cohorts."""
    base_path = Path(__file__).parent.parent / 'tmp'

    print("Testing stability calculation with train/test cohorts...")
    print(f"Dataset path: {base_path / 'dataset.csv'}")

    # Load sample
    print("\nLoading dataset sample (5,000 rows)...")
    df_full = pd.read_csv(base_path / 'dataset.csv', nrows=5000)

    print(f"Dataset shape: {df_full.shape}")
    print(f"\ndataTag distribution:")
    print(df_full['dataTag'].value_counts())

    # Save sample
    sample_csv = base_path / 'dataset_sample_stability.csv'
    df_full.to_csv(sample_csv, index=False)

    # Run EDA with stability calculation
    print("\n" + "="*80)
    print("Running EDA with stability calculation...")
    print("="*80)

    runner = EDARunner(
        calculate_stability=True,
        cohort_column='dataTag',
        baseline_cohort='training',
        comparison_cohort='test',
        max_correlation_features=50  # Limit for speed
    )

    results = runner.run(
        data=sample_csv,
        feature_metadata=base_path / 'feature_config.json',
        target_variable='target_variable',
        output_path=base_path / 'stability_test_output.json'
    )

    # Display results
    print("\n" + "="*80)
    print("HIGHEST METRICS (WITH STABILITY)")
    print("="*80)

    hm = results['highest_metrics']

    if 'highest_correlation' in hm:
        hc = hm['highest_correlation']
        print(f"\n✅ Highest Correlation: {hc['feature_name']}")
        print(f"   Value: {hc['value']}")

    if 'highest_iv' in hm:
        hi = hm['highest_iv']
        print(f"\n✅ Highest IV: {hi['feature_name']}")
        print(f"   Value: {hi['value']}")

    if 'highest_statistical_score' in hm:
        hi = hm['highest_statistical_score']
        print(f"\n✅ Highest Statistical Score: {hi['feature_name']}")
        print(f"   Score: {hi['value']}")

    if 'highest_stability' in hm:
        hs = hm['highest_stability']
        print(f"\n✅ Highest Stability:")
        if hs.get('feature_name'):
            print(f"   Feature: {hs['feature_name']}")
            print(f"   PSI: {hs['value']} ({hs.get('stability', 'N/A')})")
            print(f"   Interpretation: {hs.get('interpretation', 'N/A')}")
        else:
            print(f"   Status: {hs.get('note', 'Not available')}")

    print("\n" + "="*80)
    print("✅ Test completed!")
    print(f"Output saved to: {base_path / 'stability_test_output.json'}")


if __name__ == '__main__':
    test_stability()
