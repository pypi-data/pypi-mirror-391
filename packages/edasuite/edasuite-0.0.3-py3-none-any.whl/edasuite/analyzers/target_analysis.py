"""Target relationship analysis including IV and WoE calculation."""

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from scipy import stats

from edasuite.core.logging_config import get_logger
from edasuite.output.formatter import safe_round

# Setup module logger
logger = get_logger(__name__)


class TargetAnalyzer:
    """Analyzer for target variable relationships."""

    def __init__(self, min_bin_size: float = 0.05, max_bins: int = 10):
        """
        Initialize target analyzer.

        Args:
            min_bin_size: Minimum bin size as fraction of total (default 5%)
            max_bins: Maximum number of bins for continuous variables
        """
        self.min_bin_size = min_bin_size
        self.max_bins = max_bins

    def analyze_target_relationship(
        self,
        feature_series: pd.Series,
        target_series: pd.Series,
        feature_type: str
    ) -> Dict[str, Any]:
        """
        Analyze relationship between feature and target variable.

        Args:
            feature_series: Feature values
            target_series: Target variable values (binary)
            feature_type: 'continuous' or 'categorical'

        Returns:
            Dictionary with correlation, IV, WoE, and predictive power
        """
        result = {
            "target_variable": target_series.name,
            "correlation_pearson": None,
            "correlation_pearson_pvalue": None,
            "correlation_spearman": None,
            "correlation_spearman_pvalue": None,
            "information_value": None,
            "predictive_power": None,
            "woe_mapping": None,
            "iv_contribution": None
        }

        # Remove rows where either feature or target is missing
        valid_idx = feature_series.notna() & target_series.notna()
        feature_clean = feature_series[valid_idx]
        target_clean = target_series[valid_idx]

        if len(feature_clean) < 10:  # Need minimum sample size
            return result

        # Check if target is binary
        unique_targets = target_clean.nunique()
        if unique_targets != 2:
            # IV only works for binary classification
            result["note"] = f"Target has {unique_targets} unique values. IV requires binary target."

        # Compute correlations
        if feature_type == "continuous":
            result.update(self._compute_correlations(feature_clean, target_clean))

        # Compute Information Value and WoE
        if unique_targets == 2:
            if feature_type == "continuous":
                iv_result = self._compute_iv_continuous(feature_clean, target_clean)
            else:  # categorical
                iv_result = self._compute_iv_categorical(feature_clean, target_clean)

            result.update(iv_result)

            # Classify predictive power based on IV
            result["predictive_power"] = self._classify_predictive_power(
                result["information_value"]
            )

        return result

    def _compute_correlations(
        self,
        feature: pd.Series,
        target: pd.Series
    ) -> Dict[str, Any]:
        """Compute Pearson and Spearman correlations with p-values."""
        import warnings
        result = {}

        # Check if feature is constant (no variance)
        if feature.nunique() <= 1:
            logger.debug("Skipping correlation for constant feature: {feature.name}")
            result["correlation_pearson"] = None
            result["correlation_pearson_pvalue"] = None
            result["correlation_spearman"] = None
            result["correlation_spearman_pvalue"] = None
            return result

        try:
            # Pearson correlation - suppress ConstantInputWarning
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', category=RuntimeWarning)
                pearson_corr, pearson_pval = stats.pearsonr(feature, target)
                if w:
                    logger.debug("Suppressed ConstantInputWarning for Pearson correlation on feature: {feature.name}")
            result["correlation_pearson"] = safe_round(pearson_corr, 4)
            result["correlation_pearson_pvalue"] = safe_round(pearson_pval, 4)
        except Exception:
            result["correlation_pearson"] = None
            result["correlation_pearson_pvalue"] = None

        try:
            # Spearman correlation - suppress ConstantInputWarning
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings('ignore', category=RuntimeWarning)
                spearman_corr, spearman_pval = stats.spearmanr(feature, target)
                if w:
                    logger.debug("Suppressed ConstantInputWarning for Spearman correlation on feature: {feature.name}")
            result["correlation_spearman"] = safe_round(spearman_corr, 4)
            result["correlation_spearman_pvalue"] = safe_round(spearman_pval, 4)
        except Exception:
            result["correlation_spearman"] = None
            result["correlation_spearman_pvalue"] = None

        return result

    def _compute_iv_continuous(
        self,
        feature: pd.Series,
        target: pd.Series
    ) -> Dict[str, Any]:
        """
        Compute Information Value for continuous features.
        Uses optimal binning based on quantiles.
        """
        # Bin the continuous feature
        try:
            # Use quantile-based binning
            binned_feature, bin_edges = pd.qcut(
                feature,
                q=min(self.max_bins, len(feature.unique())),
                duplicates='drop',
                retbins=True
            )
        except Exception:
            # Fall back to equal-width binning if quantile fails
            try:
                binned_feature, bin_edges = pd.cut(
                    feature,
                    bins=self.max_bins,
                    duplicates='drop',
                    retbins=True
                )
            except Exception:
                return {
                    "information_value": None,
                    "woe_mapping": None,
                    "iv_contribution": None
                }

        # Compute IV for binned feature
        return self._compute_iv_categorical(binned_feature, target)

    def _compute_iv_categorical(
        self,
        feature: pd.Series,
        target: pd.Series
    ) -> Dict[str, Any]:
        """
        Compute Information Value and WoE for categorical features.

        IV = Σ (% of goods - % of bads) * WoE
        WoE = ln(% of goods / % of bads)
        """
        # Create crosstab
        df = pd.DataFrame({'feature': feature, 'target': target})

        # Get counts of goods (0) and bads (1)
        crosstab = pd.crosstab(df['feature'], df['target'])

        # Handle case where target only has one class in some bins
        if crosstab.shape[1] < 2:
            return {
                "information_value": None,
                "woe_mapping": None,
                "iv_contribution": None
            }

        # Assume binary target: column 0 is good, column 1 is bad
        # Get the actual column names (could be 0/1, True/False, etc.)
        cols = sorted(crosstab.columns)
        goods_col = cols[0]  # Typically 0 or False (negative class)
        bads_col = cols[1]   # Typically 1 or True (positive class)

        goods = crosstab[goods_col]
        bads = crosstab[bads_col]

        # Calculate distributions
        total_goods = goods.sum()
        total_bads = bads.sum()

        if total_goods == 0 or total_bads == 0:
            return {
                "information_value": None,
                "woe_mapping": None,
                "iv_contribution": None
            }

        # Calculate WoE and IV for each category
        woe_mapping = {}
        iv_contribution = {}
        total_iv = 0.0

        for category in crosstab.index:
            good_count = goods[category]
            bad_count = bads[category]

            # Avoid division by zero - add small constant
            good_pct = (good_count + 0.5) / (total_goods + 0.5)
            bad_pct = (bad_count + 0.5) / (total_bads + 0.5)

            # WoE = ln(% of goods / % of bads)
            woe = np.log(good_pct / bad_pct)

            # IV contribution = (% of goods - % of bads) * WoE
            iv_contrib = (good_pct - bad_pct) * woe

            woe_mapping[str(category)] = safe_round(woe, 4)
            iv_contribution[str(category)] = safe_round(iv_contrib, 4)
            total_iv += iv_contrib

        # Add default WoE for unseen categories (use 0)
        woe_mapping["_default"] = 0.0

        return {
            "information_value": safe_round(total_iv, 4),
            "woe_mapping": woe_mapping,
            "iv_contribution": iv_contribution
        }

    def _classify_predictive_power(self, iv: Optional[float]) -> Optional[str]:
        """
        Classify predictive power based on Information Value.

        IV < 0.02: Unpredictive
        0.02 <= IV < 0.1: Weak
        0.1 <= IV < 0.3: Medium
        0.3 <= IV < 0.5: Strong
        IV >= 0.5: Very Strong / Suspicious
        """
        if iv is None:
            return None

        if iv < 0.02:
            return "unpredictive"
        elif iv < 0.1:
            return "weak"
        elif iv < 0.3:
            return "medium"
        elif iv < 0.5:
            return "strong"
        else:
            return "very_strong"

    def compute_vif(self, df: pd.DataFrame, feature_col: str) -> Optional[float]:
        """
        Compute Variance Inflation Factor for a feature.

        VIF = 1 / (1 - R²)
        where R² is from regressing this feature on all other features.

        Args:
            df: DataFrame with numeric features
            feature_col: Feature to compute VIF for

        Returns:
            VIF value or None if cannot compute
        """
        try:
            from sklearn.linear_model import LinearRegression

            # Get all numeric columns except the feature
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if feature_col not in numeric_cols:
                return None

            other_cols = [col for col in numeric_cols if col != feature_col]
            if len(other_cols) < 1:
                return None

            # Prepare data
            X = df[other_cols].fillna(df[other_cols].mean())
            y = df[feature_col].fillna(df[feature_col].mean())

            # Fit regression
            model = LinearRegression()
            model.fit(X, y)

            # Calculate R²
            r_squared = model.score(X, y)

            # Calculate VIF
            if r_squared >= 0.9999:  # Avoid division by near-zero
                return None

            vif = 1 / (1 - r_squared)
            return safe_round(vif, 2)

        except Exception:
            return None
