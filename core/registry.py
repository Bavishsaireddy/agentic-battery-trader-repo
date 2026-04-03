"""
core/registry.py — ToolRegistry
Decorator-based tool registration.  Every decorated function is automatically
introspected for its docstring and type hints so the LLM planner receives a
well-formed tool spec without any manual JSON authoring.
"""

from __future__ import annotations

import inspect
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

# Python → JSON Schema type mapping (simplified for tool use)
_PY_TO_JSON = {
    "str": "string",
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "DataFrame": "object",
    "dict": "object",
    "list": "array",
    "NoneType": "null",
}


class ToolRegistry:
    """Singleton registry that collects tool callables and their LLM specs."""

    _instance: "ToolRegistry | None" = None

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, Callable] = {}
            cls._instance._specs: List[Dict[str, Any]] = []
        return cls._instance

    # ── decorator -------------------------------------------------------------

    def register(self, fn: Callable) -> Callable:
        """Decorator: register *fn* and auto-generate its LLM tool spec."""
        name = fn.__name__
        if name in self._tools:
            logger.warning("Tool '%s' already registered — overwriting.", name)
        self._tools[name] = fn
        self._specs.append(self._build_spec(fn))
        logger.debug("Registered tool: %s", name)
        return fn

    # ── public API ------------------------------------------------------------

    def get(self, name: str) -> Callable:
        if name not in self._tools:
            raise KeyError(f"Unknown tool '{name}'. Registered: {list(self._tools)}")
        return self._tools[name]

    @property
    def tool_specs(self) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible function specs for all registered tools."""
        return list(self._specs)

    @property
    def names(self) -> List[str]:
        return list(self._tools.keys())

    # ── introspection ---------------------------------------------------------

    def _build_spec(self, fn: Callable) -> Dict[str, Any]:
        sig   = inspect.signature(fn)
        hints = fn.__annotations__
        doc   = inspect.getdoc(fn) or ""

        properties: Dict[str, Any] = {}
        required: List[str] = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            json_type = _PY_TO_JSON.get(
                hints.get(param_name, type(None)).__name__
                if hasattr(hints.get(param_name, None), "__name__")
                else "object",
                "object",
            )
            properties[param_name] = {"type": json_type}

            # If no default → required
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": doc.splitlines()[0] if doc else "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


# Module-level singleton — import and use directly
registry = ToolRegistry()
