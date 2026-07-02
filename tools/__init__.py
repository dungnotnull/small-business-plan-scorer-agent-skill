"""small-business-plan-scorer tooling package.

Exports the deterministic feasibility scorer and the weekly knowledge updater.
Importable as `small_business_plan_scorer` when installed (see pyproject.toml),
or directly as top-level modules from the `tools/` directory otherwise.
"""

from __future__ import annotations

from . import knowledge_updater, scoring_engine  # noqa: F401

__all__ = ["scoring_engine", "knowledge_updater"]
__version__ = "1.0.0"
