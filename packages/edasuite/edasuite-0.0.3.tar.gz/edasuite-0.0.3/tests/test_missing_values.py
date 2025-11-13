"""Test missing value handling and provider match rates."""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from edasuite.core.missing import replace_sentinel_values_with_nulls, compute_provider_match_rates

def test_sentinel_replacement():
    """Test replacing sentinel values with nulls."""
    print("=" * 80)
    print("TEST: Sentinel Value Replacement")
    print("=" * 80)

    # Create test data
    df = pd.DataFrame({
        'age': [25, -1, 30, -1, 35],
        'income': [50000, 60000, -1, 70000, -1],
        'name': ['Alice', '', 'Bob', '', 'Charlie'],
        'city': ['NYC', 'LA', '', 'SF', 'NYC']
    })

    metadata = {
        'features': [
            {'name': 'age', 'no_hit_value': '-1'},
            {'name': 'income', 'no_hit_value': '-1'},
            {'name': 'name', 'no_hit_value': ''},
            {'name': 'city', 'no_hit_value': ''}
        ]
    }

    print("\nOriginal data:")
    print(df)
    print(f"\nNull counts before: {df.isna().sum().to_dict()}")

    # Replace sentinels
    df_clean = replace_sentinel_values_with_nulls(df, metadata)

    print(f"\nNull counts after: {df_clean.isna().sum().to_dict()}")
    print("\nCleaned data:")
    print(df_clean)

    # Verify
    assert df_clean['age'].isna().sum() == 2, "Should have 2 nulls in age"
    assert df_clean['income'].isna().sum() == 2, "Should have 2 nulls in income"
    assert df_clean['name'].isna().sum() == 2, "Should have 2 nulls in name"
    assert df_clean["city"].isna().sum() == 1, "Should have 1 null in city"

    print("\n✅ Sentinel replacement test passed!")


def test_provider_match_rates():
    """Test computing provider match rates."""
    print("\n" + "=" * 80)
    print("TEST: Provider Match Rates")
    print("=" * 80)

    # Create test data (already cleaned)
    df = pd.DataFrame({
        'age': [25, None, 30, None, 35],
        'income': [50000, 60000, None, 70000, None],
        'name': ['Alice', None, 'Bob', None, 'Charlie'],
        'credit_score': [700, 750, None, 680, None]
    })

    metadata = {
        'features': [
            {'name': 'age', 'source': {'provider': 'bureau'}},
            {'name': 'income', 'source': {'provider': 'bureau'}},
            {'name': 'name', 'source': {'provider': 'kyc'}},
            {'name': 'credit_score', 'source': {'provider': 'bureau'}}
        ]
    }

    print("\nData (5 records):")
    print(df)

    # Compute match rates
    provider_stats = compute_provider_match_rates(df, metadata)

    print("\nProvider match rates:")
    for provider, stats in provider_stats.items():
        print(f"\n{provider}:")
        print(f"  Match rate: {stats['match_rate']:.1%}")
        print(f"  Total features: {stats['total_features']}")
        print(f"  Matched records: {stats['matched_records']}/{stats['total_records']}")
        print(f"  Feature match rates:")
        for feat, rate in stats['feature_match_rates'].items():
            print(f"    {feat}: {rate:.1%}")

    # Verify bureau: 3 features, 4/5 records have at least one bureau feature
    assert provider_stats['bureau']['total_features'] == 3
    assert provider_stats["bureau"]["matched_records"] == 5  # All records have at least one bureau value
    
    # Verify KYC: 1 feature, 3/5 records have name
    assert provider_stats['kyc']['total_features'] == 1
    assert provider_stats['kyc']['matched_records'] == 3

    print("\n✅ Provider match rates test passed!")


def test_with_real_data():
    """Test with real dataset sample."""
    print("\n" + "=" * 80)
    print("TEST: Real Data")
    print("=" * 80)

    base_path = Path(__file__).parent.parent / 'tmp'

    # Load small sample
    print("\nLoading dataset sample...")
    df = pd.read_csv(base_path / 'dataset.csv', nrows=1000)

    # Load metadata
    import json
    with open(base_path / 'feature_config.json') as f:
        metadata = json.load(f)

    # Check before
    null_counts_before = df.isna().sum().sum()
    print(f"Total nulls before: {null_counts_before:,}")

    # Replace sentinels
    df_clean = replace_sentinel_values_with_nulls(df, metadata)

    # Check after
    null_counts_after = df_clean.isna().sum().sum()
    print(f"Total nulls after: {null_counts_after:,}")
    print(f"Replaced: {null_counts_after - null_counts_before:,} sentinel values")

    # Compute provider stats
    provider_stats = compute_provider_match_rates(df_clean, metadata)

    print(f"\nProviders found: {len(provider_stats)}")
    if provider_stats:
        print("\nTop 5 providers by match rate:")
        sorted_providers = sorted(provider_stats.items(), key=lambda x: x[1]['match_rate'], reverse=True)
        for provider, stats in sorted_providers[:5]:
            print(f"  {provider:30} {stats['match_rate']:6.1%}  ({stats['total_features']} features)")

    print("\n✅ Real data test passed!")


if __name__ == '__main__':
    test_sentinel_replacement()
    test_provider_match_rates()
    test_with_real_data()
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
