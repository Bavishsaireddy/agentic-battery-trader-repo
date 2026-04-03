"""
core/evidence.py — EvidenceStore
A lightweight key-value store that holds the outputs of every tool run.
Serialises cleanly to JSON so the LLM analyser can consume the full evidence
bundle as a single prompt payload.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class EvidenceStore:
    """Accumulates tool results and exposes them as a JSON-serialisable dict."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    # ── mutation ---------------------------------------------------------------

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key*, converting DataFrames automatically."""
        self._data[key] = self._coerce(value)
        logger.debug("Evidence stored: %s", key)

    # ── access -----------------------------------------------------------------

    def get(self, key: str) -> Any:
        return self._data[key]

    def keys(self) -> List[str]:
        return list(self._data.keys())

    def as_dict(self) -> Dict[str, Any]:
        """Return a plain dict (all values already JSON-safe)."""
        return dict(self._data)

    def to_json(self, indent: int = 2) -> str:
        """Serialise the entire store to a JSON string."""
        return json.dumps(self._data, indent=indent, default=str)

    def __repr__(self) -> str:  # noqa: D105
        return f"EvidenceStore(keys={self.keys()})"

    # ── helpers ---------------------------------------------------------------

    @staticmethod
    def _coerce(value: Any) -> Any:
        """Convert pandas objects to JSON-serialisable equivalents."""
        if isinstance(value, pd.DataFrame):
            return value.to_dict(orient="records")
        if isinstance(value, pd.Series):
            return value.to_dict()
        return value
