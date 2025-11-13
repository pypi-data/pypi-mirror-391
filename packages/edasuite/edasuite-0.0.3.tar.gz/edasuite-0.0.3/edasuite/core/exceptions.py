"""Custom exception hierarchy for EDASuite.

This module defines domain-specific exceptions that provide better error
handling and more informative error messages throughout the EDASuite library.
"""


class EDASuiteError(Exception):
    """Base exception for all EDASuite errors.

    All custom exceptions in EDASuite inherit from this base class.
    This allows users to catch all EDASuite-specific errors with a single
    except clause if needed.

    Example:
        >>> try:
        ...     runner.run(df)
        ... except EDASuiteError as e:
        ...     print(f"EDASuite error: {e}")
    """
    pass


class DataLoadError(EDASuiteError):
    """Error loading or reading data.

    Raised when there are issues loading data from files, URLs, or other sources.

    Example:
        >>> raise DataLoadError("Failed to load CSV: file not found")
    """
    pass


class DataValidationError(EDASuiteError):
    """Data validation error.

    Raised when data doesn't meet expected validation criteria, such as:
    - Missing required columns
    - Invalid data types
    - Out-of-range values
    - Insufficient data for analysis

    Example:
        >>> raise DataValidationError("Target column 'target' not found in dataset")
    """
    pass


class AnalysisError(EDASuiteError):
    """Error during analysis computation.

    Raised when statistical or analytical computations fail, such as:
    - Correlation calculation errors
    - Statistical test failures
    - Invalid analysis parameters

    Example:
        >>> raise AnalysisError("Cannot compute correlation: insufficient variance")
    """
    pass


class ConfigurationError(EDASuiteError):
    """Configuration error.

    Raised when invalid configuration parameters are provided, such as:
    - Invalid parameter values
    - Conflicting configuration options
    - Missing required configuration

    Example:
        >>> raise ConfigurationError("max_categories must be positive integer")
    """
    pass


class FeatureTypeError(EDASuiteError):
    """Error related to feature type detection or handling.

    Raised when there are issues with feature type detection or when
    operations are performed on incompatible feature types.

    Example:
        >>> raise FeatureTypeError("Cannot compute IV for datetime features")
    """
    pass


class MissingDataError(EDASuiteError):
    """Error related to missing data handling.

    Raised when missing data causes analysis to fail or when
    missing data handling configuration is invalid.

    Example:
        >>> raise MissingDataError("Cannot analyze: all values are missing")
    """
    pass


class StabilityAnalysisError(EDASuiteError):
    """Error during stability analysis.

    Raised when stability calculations (PSI, CSI) fail, such as:
    - Insufficient cohort sizes
    - Missing cohort columns
    - Invalid time periods

    Example:
        >>> raise StabilityAnalysisError("Baseline cohort has only 10 samples, requires at least 100")
    """
    pass


class OutputFormattingError(EDASuiteError):
    """Error during output formatting or serialization.

    Raised when there are issues formatting or serializing analysis results,
    such as JSON serialization errors or invalid output configurations.

    Example:
        >>> raise OutputFormattingError("Cannot serialize NaN values without sanitization")
    """
    pass


class TargetAnalysisError(EDASuiteError):
    """Error during target variable analysis.

    Raised when target relationship analysis fails, such as:
    - Invalid target variable
    - Binary target required but multi-class found
    - Insufficient samples for IV calculation

    Example:
        >>> raise TargetAnalysisError("IV calculation requires binary target, found 5 classes")
    """
    pass
