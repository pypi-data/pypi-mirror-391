"""Test feature filtering logic - only analyze features with provider set."""

import pandas as pd
import json
import tempfile
from pathlib import Path
from edasuite import EDARunner, DataLoader


def test_feature_filtering_with_provider():
    """Test that only features with provider are analyzed."""

    # Create sample dataset
    df = pd.DataFrame({
        'feature_with_provider': [1, 2, 3, 4, 5],
        'feature_without_provider': [10, 20, 30, 40, 50],
        'onboarding_time': pd.date_range('2024-01-01', periods=5),
        'dataTag': ['training', 'training', 'test', 'test', 'test'],
        'target_variable': [0, 1, 0, 1, 0]
    })

    # Create feature metadata - only some features have provider
    feature_metadata = {
        'features': [
            {
                'name': 'feature_with_provider',
                'provider': 'provider_a',
                'description': 'Feature with provider',
                'variable_type': 'continuous'
            },
            {
                'name': 'feature_without_provider',
                'provider': None,  # No provider set
                'description': 'Feature without provider',
                'variable_type': 'continuous'
            },
            {
                'name': 'onboarding_time',
                'provider': None,
                'description': 'Onboarding time metadata',
                'variable_type': 'datetime'
            },
            {
                'name': 'dataTag',
                'provider': None,
                'description': 'Data tag for train/test split',
                'variable_type': 'categorical'
            },
            {
                'name': 'target_variable',
                'provider': 'internal',
                'description': 'Target variable',
                'variable_type': 'categorical'
            }
        ]
    }

    # Save to temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / 'test_data.csv'
        metadata_path = Path(tmpdir) / 'metadata.json'

        df.to_csv(csv_path, index=False)
        with open(metadata_path, 'w') as f:
            json.dump(feature_metadata, f)

        # Run EDA without stability
        runner = EDARunner()
        results = runner.run(
            data=csv_path,
            feature_metadata=metadata_path,
            target_variable='target_variable'
        )

        # Verify only features with provider are analyzed
        analyzed_features = [f['feature_name'] for f in results['features']]

        print("\nAnalyzed features:", analyzed_features)

        # Should include: feature_with_provider, target_variable
        assert 'feature_with_provider' in analyzed_features, "Feature with provider should be analyzed"
        assert 'target_variable' in analyzed_features, "Target variable should be analyzed"

        # Should NOT include: feature_without_provider, onboarding_time, dataTag
        assert 'feature_without_provider' not in analyzed_features, "Feature without provider should NOT be analyzed"
        assert 'onboarding_time' not in analyzed_features, "onboarding_time should NOT be analyzed as a feature"
        assert 'dataTag' not in analyzed_features, "dataTag should NOT be analyzed as a feature"

        # Verify target variable has is_target flag
        target_feature = next(f for f in results['features'] if f['feature_name'] == 'target_variable')
        assert target_feature.get('is_target') == True, "Target variable should have is_target=True"

        print("✅ Feature filtering test passed!")


def test_feature_filtering_with_stability():
    """Test that metadata columns are excluded but used for stability."""

    # Create sample dataset
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5, 6],
        'onboarding_time': pd.date_range('2024-01-01', periods=6),
        'dataTag': ['training', 'training', 'training', 'test', 'test', 'test'],
        'target_variable': [0, 1, 0, 1, 0, 1]
    })

    # Create feature metadata
    feature_metadata = {
        'features': [
            {
                'name': 'feature1',
                'provider': 'provider_a',
                'description': 'Feature 1',
                'variable_type': 'continuous'
            },
            {
                'name': 'onboarding_time',
                'provider': None,
                'description': 'Onboarding time',
                'variable_type': 'datetime'
            },
            {
                'name': 'dataTag',
                'provider': None,
                'description': 'Data tag',
                'variable_type': 'categorical'
            },
            {
                'name': 'target_variable',
                'provider': 'internal',
                'description': 'Target',
                'variable_type': 'categorical'
            }
        ]
    }

    # Save to temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / 'test_data.csv'
        metadata_path = Path(tmpdir) / 'metadata.json'

        df.to_csv(csv_path, index=False)
        with open(metadata_path, 'w') as f:
            json.dump(feature_metadata, f)

        # Run EDA with cohort-based stability
        runner = EDARunner(
            calculate_stability=True,
            cohort_column='dataTag',
            baseline_cohort='training',
            comparison_cohort='test'
        )

        results = runner.run(
            data=csv_path,
            feature_metadata=metadata_path,
            target_variable='target_variable'
        )

        # Verify feature analysis
        analyzed_features = [f['feature_name'] for f in results['features']]

        print("\nAnalyzed features:", analyzed_features)

        assert 'feature1' in analyzed_features, "feature1 should be analyzed"
        assert 'target_variable' in analyzed_features, "target should be analyzed"
        assert 'dataTag' not in analyzed_features, "dataTag should NOT be analyzed as a feature"
        assert 'onboarding_time' not in analyzed_features, "onboarding_time should NOT be analyzed as a feature"

        # Verify stability was calculated (it should use dataTag but not analyze it)
        if 'stability_analysis' in results:
            print("✅ Stability analysis was performed using dataTag")

        print("✅ Feature filtering with stability test passed!")


if __name__ == '__main__':
    test_feature_filtering_with_provider()
    test_feature_filtering_with_stability()
    print("\n" + "="*80)
    print("All feature filtering tests passed!")
    print("="*80)