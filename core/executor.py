"""
core/executor.py — ToolExecutor
Receives an ordered execution plan (list of tool-call dicts) from the planner,
dispatches each call through the registry, isolates errors so one bad tool
does not abort the whole run, and accumulates results in an EvidenceStore.
"""

from __future__ import annotations

import logging
import traceback
from typing import Any, Dict, List

import pandas as pd

from core.registry import ToolRegistry
from core.evidence import EvidenceStore

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Execute a tool plan and populate an EvidenceStore."""

    def __init__(self, registry: ToolRegistry, df: pd.DataFrame) -> None:
        self.registry = registry
        self.df = df
        self.store = EvidenceStore()

    # ── public ----------------------------------------------------------------

    def run(self, plan: List[Dict[str, Any]]) -> EvidenceStore:
        """
        Execute every step in *plan*.

        Each step is a dict with at minimum:
            { "tool": "<registered_name>", "args": {...} }

        Results land in self.store keyed by tool name.
        Errors are captured as {"error": "<message>"} — never re-raised.
        """
        logger.info("Executing %d tool(s) from plan.", len(plan))
        for step in plan:
            self._execute_step(step)
        logger.info("Execution complete. Evidence keys: %s", self.store.keys())
        return self.store

    # ── private ---------------------------------------------------------------

    def _execute_step(self, step: Dict[str, Any]) -> None:
        tool_name = step.get("tool", "")
        args: Dict[str, Any] = step.get("args", {})

        logger.info("→ Running tool: %s  args=%s", tool_name, args)

        try:
            fn = self.registry.get(tool_name)
            # The LLM sometimes includes 'df' in the args since it sees it in the spec.
            # We always inject self.df as the first positional argument so we strip it out here.
            args.pop("df", None)
            result = fn(self.df, **args)
            self.store.set(tool_name, result)
            logger.info("  ✓ %s succeeded.", tool_name)
        except KeyError as exc:
            msg = f"Tool not found: {exc}"
            logger.error("  ✗ %s", msg)
            self.store.set(tool_name, {"error": msg})
        except Exception:
            tb = traceback.format_exc()
            logger.error("  ✗ %s raised an exception:\n%s", tool_name, tb)
            self.store.set(tool_name, {"error": tb})
