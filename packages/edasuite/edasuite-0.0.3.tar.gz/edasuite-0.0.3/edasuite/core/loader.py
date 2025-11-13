"""Data loading and validation utilities."""

import json
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd

from edasuite.core.types import FeatureMetadata


class DataLoader:
    """Handles loading and validation of datasets."""

    @staticmethod
    def load_csv(
        filepath: Union[str, Path],
        sample_size: Optional[int] = None,
        use_chunking: Optional[bool] = None,
        chunk_size: int = 50000,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load CSV file with optional sampling and chunking for large files.

        Args:
            filepath: Path to CSV file
            sample_size: Optional number of rows to sample
            use_chunking: Force chunking on/off. If None, auto-detect based on file size
            chunk_size: Number of rows per chunk when using chunking
            **kwargs: Additional arguments for pd.read_csv

        Returns:
            Loaded DataFrame
        """
        from edasuite.core.logging_config import get_logger
        from edasuite.core.performance import ChunkedCSVReader, should_use_chunking

        logger = get_logger(__name__)
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        # Auto-detect chunking if not specified
        if use_chunking is None:
            use_chunking = should_use_chunking(filepath, threshold_mb=100.0)
            if use_chunking:
                logger.info(f"Large file detected ({filepath.stat().st_size / 1024 / 1024:.1f} MB), using chunked reading")

        # Use chunked reading for large files
        if use_chunking:
            reader = ChunkedCSVReader(filepath, chunksize=chunk_size, sample_size=sample_size)
            df = reader.read_all()
        else:
            if sample_size:
                df = pd.read_csv(filepath, nrows=sample_size, **kwargs)
            else:
                df = pd.read_csv(filepath, **kwargs)

        return df

    @staticmethod
    def load_parquet(
        filepath: Union[str, Path],
        sample_size: Optional[int] = None,
        columns: Optional[list] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load Parquet file with optional column selection and sampling.

        Args:
            filepath: Path to Parquet file
            sample_size: Optional number of rows to sample
            columns: Optional list of columns to load (reduces memory usage)
            **kwargs: Additional arguments for pd.read_parquet

        Returns:
            Loaded DataFrame
        """
        from edasuite.core.logging_config import get_logger

        logger = get_logger(__name__)
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Parquet file not found: {filepath}")

        # Log file size
        file_size_mb = filepath.stat().st_size / 1024 / 1024
        logger.info(f"Loading Parquet file ({file_size_mb:.1f} MB)...")

        # Read parquet file
        try:
            df = pd.read_parquet(
                filepath,
                columns=columns,
                engine='pyarrow',
                **kwargs
            )

            # Apply sampling if requested
            if sample_size and len(df) > sample_size:
                logger.info(f"Sampling {sample_size} rows from {len(df)} total rows")
                df = df.head(sample_size)

            logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
            return df

        except ImportError as e:
            raise ImportError(
                "Parquet support requires 'pyarrow'. "
                "Install it with: pip install pyarrow"
            ) from e

    @staticmethod
    def load_feature_metadata(
        filepath: Union[str, Path]
    ) -> Dict[str, FeatureMetadata]:
        """
        Load feature metadata from JSON file.
        
        Args:
            filepath: Path to JSON file with feature metadata
            
        Returns:
            Dictionary mapping feature names to metadata
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return {}

        with open(filepath) as f:
            data = json.load(f)

        metadata = {}
        features = data.get('features', [])

        for feature in features:
            feature_obj = FeatureMetadata(
                name=feature.get('name'),
                provider=feature.get('provider'),
                description=feature.get('description'),
                variable_type=feature.get('variable_type'),
                default=feature.get('default'),
                no_hit_value=feature.get('no_hit_value')
            )
            if feature_obj.name:
                metadata[feature_obj.name] = feature_obj

        return metadata

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate DataFrame and return basic information.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        if df.empty:
            raise ValueError("DataFrame is empty")

        return {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "column_types": df.dtypes.to_dict(),
            "has_duplicates": df.duplicated().any(),
            "duplicate_count": df.duplicated().sum()
        }
