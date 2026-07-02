"""scoring_engine.py - Deterministic feasibility scorer (Idea 63).

Reference implementation for the `sub-scoring-engine` sub-skill. Given a
validated plan object, market research, and an assumption log it computes the
six framework-mapped dimension scores, applies the hard-cap rules from
SECOND-KNOWLEDGE-BRAIN.md, and produces the weighted total + feasibility band.

The math here is fully deterministic: identical inputs always yield identical
scores. The LLM sub-skill supplies qualitative judgement and evidence citations;
this module supplies the auditable arithmetic and gate enforcement.

Run:
    python tools/scoring_engine.py plan.json --research research.json \\
        --assumptions assumptions.json --out score.json

Spec: SECOND-KNOWLEDGE-BRAIN.md sections 2-3.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Dimension catalogue (single source of truth; mirrors the brain file).
# ---------------------------------------------------------------------------

DIMENSIONS = (
    {"name": "Market opportunity", "weight": 0.20, "framework": "TAM/SAM/SOM"},
    {"name": "Business-model coherence", "weight": 0.20, "framework": "BMC/Lean Canvas"},
    {"name": "Competitive position", "weight": 0.15, "framework": "Porter's Five Forces"},
    {"name": "Unit economics & financials", "weight": 0.25, "framework": "Unit economics"},
    {"name": "Operational readiness", "weight": 0.10, "framework": "Ops + SWOT"},
    {"name": "Risk & assumptions", "weight": 0.10, "framework": "SWOT + stress-test"},
)

BANDS = (
    (80, 100, "GO"),
    (65, 79, "CONDITIONAL_GO"),
    (50, 64, "PIVOT"),
    (0, 49, "NO_GO"),
)


def band_for(total: int) -> str:
    """Map a weighted total (0-100) to a feasibility band label."""
    if not 0 <= total <= 100:
        raise ValueError(f"weighted total out of range: {total}")
    for low, high, label in BANDS:
        if low <= total <= high:
            return label
    return "NO_GO"


def _clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(value)))


# ---------------------------------------------------------------------------
# Hard-cap rules. Each returns (capped_score, cap_reason or None).
# ---------------------------------------------------------------------------


def _cap_market(score: int, research: dict[str, Any]) -> tuple[int, str | None]:
    if not research.get("tam_bottom_up", False):
        return min(score, 40), "TAM not bottom-up; market score capped at 40"
    return score, None


def _cap_model(score: int, plan: dict[str, Any]) -> tuple[int, str | None]:
    canvas = plan.get("canvas", {}) or {}
    links_ok = (
        canvas.get("revenue_streams")
        and canvas.get("value_propositions")
        and canvas.get("customer_segments")
        and canvas.get("channels")
    )
    if not links_ok:
        return min(score, 50), "Revenue->VP->Segment->Channel link incomplete; capped at 50"
    return score, None


def _cap_competitive(score: int, research: dict[str, Any]) -> tuple[int, str | None]:
    porter = research.get("porter", {}) or {}
    forces = ("rivalry", "new_entrants", "substitutes", "supplier_power", "buyer_power")
    if any(force not in porter for force in forces):
        return min(score, 50), "Porter's Five Forces incomplete; competitive score capped at 50"
    return score, None


def _cap_economics(score: int, plan: dict[str, Any]) -> tuple[int, str | None]:
    pricing = plan.get("pricing", {}) or {}
    costs = plan.get("costs", {}) or {}
    price = pricing.get("price_per_unit")
    var_cost = costs.get("variable_per_unit")
    cac = costs.get("cac")
    if price is None or var_cost is None:
        return min(score, 40), "Price or variable cost missing; economics capped at 40"
    if cac is None:
        return min(score, 50), "CAC missing; economics capped at 50"
    return score, None


def _cap_ops(score: int, plan: dict[str, Any]) -> tuple[int, str | None]:
    canvas = plan.get("canvas", {}) or {}
    capital = plan.get("capital", {}) or {}
    has_team = bool(canvas.get("key_resources") or canvas.get("key_activities"))
    has_ops = bool(capital.get("monthly_burn") is not None or canvas.get("key_activities"))
    if not has_team or not has_ops:
        return min(score, 60), "No team/ops plan; operational readiness capped at 60"
    return score, None


def _cap_risk(score: int, assumptions: dict[str, Any]) -> tuple[int, str | None]:
    count = len(assumptions.get("assumptions", []) or [])
    if count < 5:
        return min(score, 50), f"Only {count} assumptions tested (<5); risk capped at 50"
    return score, None


# ---------------------------------------------------------------------------
# Rubric band helpers (0-100 per dimension).
# ---------------------------------------------------------------------------


def _market_score(research: dict[str, Any]) -> int:
    """Score market opportunity from the bottom-up TAM + SOM capture basis."""
    if not research.get("tam_bottom_up", False):
        return 35
    cited = sum(1 for m in ("buyers", "frequency", "avg_price") if research.get(m) is not None)
    som_basis = bool(research.get("som_capture_basis"))
    growth_dated = bool(research.get("growth_trend_dated"))
    if cited == 3 and som_basis and growth_dated:
        return 90
    if cited == 3 and som_basis:
        return 78
    if cited >= 2:
        return 62
    return 45


def _model_score(plan: dict[str, Any]) -> int:
    canvas = plan.get("canvas", {}) or {}
    blocks = (
        "customer_segments",
        "value_propositions",
        "channels",
        "customer_relationships",
        "revenue_streams",
        "key_resources",
        "key_activities",
        "key_partnerships",
        "cost_structure",
    )
    filled = sum(1 for b in blocks if canvas.get(b))
    if filled == 9:
        return 90
    if filled >= 8:
        return 76
    if filled >= 7:
        return 60
    if filled >= 5:
        return 46
    if filled >= 3:
        return 30
    return 15


def _competitive_score(research: dict[str, Any]) -> int:
    """Map Porter composite attractiveness (1.0 best - 5.0 worst) to 0-100."""
    porter = research.get("porter", {}) or {}
    forces = ("rivalry", "new_entrants", "substitutes", "supplier_power", "buyer_power")
    values = [porter[f] for f in forces if f in porter]
    if len(values) != 5:
        return 30
    composite = sum(values) / 5.0
    if composite <= 1.8:
        base = 90
    elif composite <= 2.6:
        base = 76
    elif composite <= 3.4:
        base = 60
    elif composite <= 4.2:
        base = 46
    else:
        base = 30
    if research.get("differentiation_gap", False):
        base = min(base + 5, 100)
    return base


def _economics_score(plan: dict[str, Any]) -> int:
    pricing = plan.get("pricing", {}) or {}
    costs = plan.get("costs", {}) or {}
    capital = plan.get("capital", {}) or {}
    price = pricing.get("price_per_unit")
    var_cost = costs.get("variable_per_unit")
    cac = costs.get("cac")
    fixed = costs.get("fixed_monthly")
    burn = capital.get("monthly_burn")
    runway = capital.get("runway_months")

    if price is None or var_cost is None:
        return 20
    contribution = price - var_cost
    if contribution <= 0:
        return 15
    known = sum(m is not None for m in (cac, fixed, burn, runway))
    if cac is None:
        return 45
    if known >= 4:
        ltv_cac_ok = runway is not None and runway >= 12
        return 88 if ltv_cac_ok else 74
    if known >= 2:
        return 62
    return 50


def _ops_score(plan: dict[str, Any]) -> int:
    canvas = plan.get("canvas", {}) or {}
    capital = plan.get("capital", {}) or {}
    resources = canvas.get("key_resources") or []
    activities = canvas.get("key_activities") or []
    partners = canvas.get("key_partnerships") or []
    has_team = bool(resources)
    has_ops = bool(activities)
    has_runway = capital.get("runway_months") is not None
    score = 20
    if has_team:
        score += 25
    if has_ops:
        score += 25
    if has_runway:
        score += 20
    if partners:
        score += 15
    return _clamp(score)


def _risk_score(assumptions: dict[str, Any]) -> int:
    items = assumptions.get("assumptions", []) or []
    count = len(items)
    tested_with_downside = sum(1 for a in items if a.get("downside_50pct"))
    with_mitigation = sum(1 for a in items if a.get("mitigation"))
    if count >= 5 and tested_with_downside >= 5 and with_mitigation >= 5:
        return 88
    if count >= 5 and tested_with_downside >= 5:
        return 74
    if count >= 5:
        return 60
    if count >= 3:
        return 46
    if count >= 1:
        return 30
    return 15


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------


@dataclass
class DimensionScore:
    name: str
    weight: float
    score: int
    framework: str
    capped: bool
    cap_reason: str | None
    rationale: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScoreReport:
    weighted_total: int
    band: str
    dimensions: list[DimensionScore]

    def to_dict(self) -> dict[str, Any]:
        return {
            "weighted_total": self.weighted_total,
            "band": self.band,
            "dimensions": [d.to_dict() for d in self.dimensions],
        }


_CAPS = {
    "Market opportunity": _cap_market,
    "Business-model coherence": _cap_model,
    "Competitive position": _cap_competitive,
    "Unit economics & financials": _cap_economics,
    "Operational readiness": _cap_ops,
    "Risk & assumptions": _cap_risk,
}

_RAW = {
    "Market opportunity": _market_score,
    "Business-model coherence": _model_score,
    "Competitive position": _competitive_score,
    "Unit economics & financials": _economics_score,
    "Operational readiness": _ops_score,
    "Risk & assumptions": _risk_score,
}


def score_plan(
    plan: dict[str, Any],
    research: dict[str, Any] | None = None,
    assumptions: dict[str, Any] | None = None,
) -> ScoreReport:
    """Score a validated plan object end-to-end.

    Args:
        plan: validated plan object from sub-requirements-gatherer.
        research: market research (TAM/SAM/SOM, Porter). Defaults to empty.
        assumptions: assumption log from sub-quality-reviewer. Defaults to empty.

    Returns:
        ScoreReport with per-dimension scores, caps, weighted total and band.
    """
    research = research or {}
    assumptions = assumptions or {}
    ctx = {
        "Market opportunity": research,
        "Business-model coherence": plan,
        "Competitive position": research,
        "Unit economics & financials": plan,
        "Operational readiness": plan,
        "Risk & assumptions": assumptions,
    }
    dims: list[DimensionScore] = []
    weighted = 0.0
    for spec in DIMENSIONS:
        name = spec["name"]
        raw = _RAW[name](ctx[name])
        capped_score, cap_reason = _CAPS[name](_clamp(raw), ctx[name])
        capped = cap_reason is not None
        weighted += capped_score * spec["weight"]
        dims.append(
            DimensionScore(
                name=name,
                weight=spec["weight"],
                score=capped_score,
                framework=spec["framework"],
                capped=capped,
                cap_reason=cap_reason,
                rationale=f"Raw {raw}; {'capped: ' + cap_reason if capped else 'no cap'}.",
                evidence=[],
            )
        )
    total = int(round(weighted))
    return ScoreReport(weighted_total=total, band=band_for(total), dimensions=dims)


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic feasibility scorer (Idea 63).")
    p.add_argument("plan", type=pathlib.Path, help="path to plan object JSON")
    p.add_argument(
        "--research", type=pathlib.Path, default=None, help="path to market research JSON"
    )
    p.add_argument(
        "--assumptions", type=pathlib.Path, default=None, help="path to assumption log JSON"
    )
    p.add_argument(
        "--out",
        type=pathlib.Path,
        default=None,
        help="write score report JSON to this path (default: stdout)",
    )
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    plan = _load_json(args.plan)
    research = _load_json(args.research) if args.research else {}
    assumptions = _load_json(args.assumptions) if args.assumptions else {}
    report = score_plan(plan, research, assumptions)
    payload = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
        print(
            f"Wrote score report to {args.out} (total={report.weighted_total}, band={report.band})"
        )
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
