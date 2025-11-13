"""Test handling of default and no_hit values as missing values."""

import pandas as pd
import pytest

from edasuite.core.types import FeatureMetadata
from edasuite.analyzers.continuous import ContinuousAnalyzer
from edasuite.analyzers.categorical import CategoricalAnalyzer


class TestDefaultAndNoHitValues:
    """Test that default and no_hit values are treated as missing."""

    def test_continuous_with_default_value(self):
        """Test continuous feature with default value."""
        # Create test data with default value -999
        data = [1.0, 2.0, 3.0, -999.0, 4.0, 5.0, -999.0]
        series = pd.Series(data, name="test_feature")

        # Create metadata with default value
        metadata = FeatureMetadata(
            name="test_feature",
            default="-999.0"
        )

        # Analyze with metadata
        analyzer = ContinuousAnalyzer()
        result = analyzer.analyze(series, feature_metadata=metadata)

        # Check that default values are counted as missing
        # Should have 2 missing values (the two -999.0 values)
        assert result.data['missing']['count'] == 2
        assert result.data['missing']['percent'] == pytest.approx(28.57, abs=0.1)

        # Stats should only use valid values [1, 2, 3, 4, 5]
        assert result.data['stats']['count'] == 5
        assert result.data['stats']['mean'] == pytest.approx(3.0, abs=0.1)

    def test_continuous_with_no_hit_value(self):
        """Test continuous feature with no_hit value."""
        # Create test data with no_hit value 0
        data = [10.0, 20.0, 30.0, 0.0, 40.0, 50.0]
        series = pd.Series(data, name="test_feature")

        # Create metadata with no_hit value
        metadata = FeatureMetadata(
            name="test_feature",
            no_hit_value="0"
        )

        # Analyze with metadata
        analyzer = ContinuousAnalyzer()
        result = analyzer.analyze(series, feature_metadata=metadata)

        # Check that no_hit values are counted as missing
        assert result.data['missing']['count'] == 1
        assert result.data['missing']['percent'] == pytest.approx(16.67, abs=0.1)

        # Stats should only use valid values [10, 20, 30, 40, 50]
        assert result.data['stats']['count'] == 5
        assert result.data['stats']['mean'] == pytest.approx(30.0, abs=0.1)

    def test_continuous_with_both_default_and_no_hit(self):
        """Test continuous feature with both default and no_hit values."""
        # Create test data with both special values
        data = [1.0, 2.0, -999.0, 3.0, 0.0, 4.0, -999.0, 5.0]
        series = pd.Series(data, name="test_feature")

        # Create metadata with both values
        metadata = FeatureMetadata(
            name="test_feature",
            default="-999.0",
            no_hit_value="0.0"
        )

        # Analyze with metadata
        analyzer = ContinuousAnalyzer()
        result = analyzer.analyze(series, feature_metadata=metadata)

        # Check that both types are counted as missing (3 total: 2x -999, 1x 0)
        assert result.data['missing']['count'] == 3
        assert result.data['missing']['percent'] == pytest.approx(37.5, abs=0.1)

        # Stats should only use valid values [1, 2, 3, 4, 5]
        assert result.data['stats']['count'] == 5

    def test_categorical_with_default_value(self):
        """Test categorical feature with default value."""
        # Create test data with default value "unknown"
        data = ["A", "B", "C", "unknown", "A", "B", "unknown", "C"]
        series = pd.Series(data, name="test_category")

        # Create metadata with default value
        metadata = FeatureMetadata(
            name="test_category",
            default="unknown"
        )

        # Analyze with metadata
        analyzer = CategoricalAnalyzer()
        result = analyzer.analyze(series, feature_metadata=metadata)

        # Check that default values are counted as missing
        assert result.data['missing']['count'] == 2
        assert result.data['missing']['percent'] == pytest.approx(25.0, abs=0.1)

        # Stats should only use valid values
        assert result.data['stats']['count'] == 6
        assert result.data['stats']['unique'] == 3  # A, B, C

    def test_categorical_with_no_hit_value(self):
        """Test categorical feature with no_hit value."""
        # Create test data with no_hit value "N/A"
        data = ["Red", "Blue", "N/A", "Red", "Green", "N/A", "Blue"]
        series = pd.Series(data, name="test_category")

        # Create metadata with no_hit value
        metadata = FeatureMetadata(
            name="test_category",
            no_hit_value="N/A"
        )

        # Analyze with metadata
        analyzer = CategoricalAnalyzer()
        result = analyzer.analyze(series, feature_metadata=metadata)

        # Check that no_hit values are counted as missing
        assert result.data['missing']['count'] == 2
        assert result.data['missing']['percent'] == pytest.approx(28.57, abs=0.1)

        # Stats should only use valid values
        assert result.data['stats']['count'] == 5
        assert result.data['stats']['unique'] == 3  # Red, Blue, Green

    def test_no_metadata_provided(self):
        """Test that analysis works normally without metadata."""
        # Create test data with -999 value
        data = [1.0, 2.0, 3.0, -999.0, 4.0, 5.0]
        series = pd.Series(data, name="test_feature")

        # Analyze without metadata
        analyzer = ContinuousAnalyzer()
        result = analyzer.analyze(series, feature_metadata=None)

        # Without metadata, -999 should NOT be treated as missing
        assert result.data['missing']['count'] == 0
        assert result.data['stats']['count'] == 6
        # Mean should include -999
        assert result.data['stats']['mean'] < 0  # Will be negative due to -999

    def test_integer_default_value(self):
        """Test that integer default values work correctly."""
        # Create test data with integer default value
        data = [1, 2, 3, -1, 4, 5, -1, 6]
        series = pd.Series(data, name="test_feature")

        # Create metadata with integer default value
        metadata = FeatureMetadata(
            name="test_feature",
            default="-1"
        )

        # Analyze with metadata
        analyzer = ContinuousAnalyzer()
        result = analyzer.analyze(series, feature_metadata=metadata)

        # Check that -1 values are counted as missing
        assert result.data['missing']['count'] == 2
        assert result.data['stats']['count'] == 6
        assert result.data['stats']['mean'] == pytest.approx(3.5, abs=0.1)
