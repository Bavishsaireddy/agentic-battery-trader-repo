"""
core/loader.py — DataLoader
Validates that an input CSV matches the expected schema, normalises column
dtypes, and inherently pivots the tall dataset into a wide feature dataset 
split by scenario and schedule type.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

import pandas as pd

from config import REQUIRED_COLUMNS, DATETIME_COLUMN, NUMERIC_COLUMNS

logger = logging.getLogger(__name__)


class SchemaError(ValueError):
    """Raised when the input data does not satisfy the required schema."""


class DataLoader:
    """Load, validate, and internally pivot battery dispatch CSV datasets."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)

    # ── public ----------------------------------------------------------------

    def load(self) -> pd.DataFrame:
        """Return a validated, pivoted DataFrame or raise SchemaError."""
        logger.info("Loading data from %s", self.path)
        df = self._read()
        self._validate_columns(df)
        df = self._normalise_dtypes(df)
        df_pivoted = self._pivot_data(df)
        logger.info("Pivoted wide shape is %d rows × %d cols", len(df_pivoted), len(df_pivoted.columns))
        return df_pivoted

    # ── private ---------------------------------------------------------------

    def _read(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"Data file not found: {self.path}")
        try:
            return pd.read_csv(self.path)
        except Exception as exc:
            raise SchemaError(f"Could not parse CSV at {self.path}: {exc}") from exc

    def _validate_columns(self, df: pd.DataFrame) -> None:
        missing = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise SchemaError(
                f"Missing required columns: {sorted(missing)}. "
                f"Found: {sorted(df.columns.tolist())}"
            )

    def _normalise_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        # Parse timestamp
        try:
            df[DATETIME_COLUMN] = pd.to_datetime(df[DATETIME_COLUMN], utc=True)
        except Exception as exc:
            raise SchemaError(
                f"Cannot parse '{DATETIME_COLUMN}' as datetime: {exc}"
            ) from exc

        # Coerce numeric columns
        for col in NUMERIC_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    def _pivot_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pivots the tall dataset so that every timestamp has flat columns 
        prefixed with `{SCENARIO_NAME}_{SCHEDULE_TYPE}_{original_column}`.
        Example output columns: 
        - START_DATETIME
        - historical_expected_SOC
        - historical_cleared_REVENUE_ENERGY
        - perfect_cleared_PRICE_ENERGY
        """
        # Create a unified categorical column to act as the pivot header
        df["group"] = df["SCENARIO_NAME"] + "_" + df["SCHEDULE_TYPE"]
        
        # Pivot the numeric columns over the datetime index
        pivoted = df.pivot(
            index=DATETIME_COLUMN,
            columns="group",
            values=NUMERIC_COLUMNS
        )
        
        # Flatten MultiIndex columns into strings e.g. "historical_expected_SOC"
        # Output MultiIndex comes out as (value_col, group) e.g., ("SOC", "historical_expected")
        pivoted.columns = [f"{grp}_{val}" for val, grp in pivoted.columns]
        
        # Bring START_DATETIME back to a standard column instead of the index
        pivoted = pivoted.reset_index()
        
        return pivoted
