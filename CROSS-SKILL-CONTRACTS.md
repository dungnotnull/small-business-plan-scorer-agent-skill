# CROSS-SKILL-CONTRACTS.md — Shared contracts for reuse across skills

The `small-business-plan-scorer` (Idea 63) exposes two stable, versioned contracts
that other skills can consume without re-implementing the logic. Any skill in the
cluster `{57, 67, 76, 78, 107, 144}` may import `tools/scoring_engine.py` and
reuse the sub-skills below, provided it honours the schemas.

## Contract 1 — Plan Object (`sub-requirements-gatherer`)

The validated plan object is the common input to scoring, stress-testing, and
roadmap generation. It is a plain JSON dict (no Python objects), so it crosses
LLM-step and process boundaries cleanly.

```json
{
  "business": {"name": "str", "idea": "problem -> solution"},
  "canvas": {
    "type": "BMC|LeanCanvas",
    "customer_segments": [], "value_propositions": [],
    "channels": [], "customer_relationships": [],
    "revenue_streams": [], "key_resources": [],
    "key_activities": [], "key_partnerships": [],
    "cost_structure": []
  },
  "segment": {"name": "str", "geography": "str", "size_basis": "str"},
  "pricing": {"price_per_unit": "number|null", "currency": "str"},
  "costs": {"variable_per_unit": "number|null", "fixed_monthly": "number|null", "cac": "number|null"},
  "capital": {"cash": "number|null", "monthly_burn": "number|null", "runway_months": "number|null"},
  "goals": {"horizon_months": "int|null", "outcome": "launch|loan|raise|validate"},
  "gaps": ["str"],
  "field_status": {"field": "provided|inferred|missing"}
}
```
**Stability:** additions are backward-compatible (new optional keys only); no key
is removed without a major-version bump. Consumers MUST tolerate unknown extra keys
(forward compatibility).

## Contract 2 — Score Object (`sub-scoring-engine` / `tools/scoring_engine.py`)

```json
{
  "weighted_total": "int 0-100",
  "band": "GO|CONDITIONAL_GO|PIVOT|NO_GO",
  "dimensions": [
    {"name": "str", "weight": "float", "score": "int",
     "framework": "str", "capped": "bool", "cap_reason": "str|null",
     "rationale": "str", "evidence": ["str"]}
  ]
}
```
**Reference implementation:** `tools/scoring_engine.py::score_plan(plan, research, assumptions)`
is deterministic and unit-tested (`tests/test_scoring_engine.py`). Reuse it directly
rather than reimplementing the weighting; this guarantees identical verdicts across
skills that share the same plan.

## Contract 3 — Assumption Log (`sub-quality-reviewer`)

```json
{
  "assumptions": [
    {"name": "str", "stated_value": "str", "basis": "cite|no basis",
     "downside_50pct": "str", "downside_effect": "str",
     "critical": "bool", "mitigation": "str"}
  ],
  "combined_worst_case": {"breakeven_months": "int|null",
                          "runway_months": "int|null", "survives": "bool"}
}
```

## Contract 4 — Roadmap Object (`sub-improvement-roadmap`)

```json
{
  "verdict": "GO|CONDITIONAL_GO|PIVOT|NO_GO",
  "verdict_rationale": "str",
  "improvements": [
    {"dimension": "str", "assumption": "str", "action": "str",
     "effort": "S|M|L", "impact": "Low|Med|High",
     "milestone": "str", "deadline": "YYYY-MM-DD"}
  ]
}
```

## Reuse map by sibling skill

| Skill idea | Reuse | How |
|-----------|-------|-----|
| 57 (business-strategy advisor) | Plan + Score object | Import `scoring_engine.score_plan` for feasibility of strategy options |
| 67 (market-entry analyzer) | Score `Competitive position` + `Market opportunity` | Reuse Porter + TAM/SAM/SOM rubrics; same score schema |
| 76 (startup pitch evaluator) | Full score + assumption log | Same four contracts end-to-end |
| 78 (SME loan advisor) | Score + roadmap | `goals.outcome="loan"`; verdict feeds loan recommendation |
| 107 (pivot/repositioning coach) | Roadmap object | Consume `improvements` + verdict to drive pivot plan |
| 144 (unit-economics calculator) | Plan object (pricing/costs/capital) + economics dimension | Reuse `_economics_score` + cap rules |

## Compatibility rules
1. Consumers MUST NOT mutate the plan object in place; copy before extending.
2. Consumers MUST pass `research` and `assumptions` as separate dicts (not stuffed into the plan).
3. Any new dimension MUST be added to `DIMENSIONS` with a weight and a cap function; weights MUST sum to 1.0 (enforced by `tests/test_scoring_engine.py`).
4. Verdict labels are an enum; do not introduce new labels without bumping the contract version.

## Versioning
Contracts are versioned in `SECOND-KNOWLEDGE-BRAIN.md` (`Version: 1.0.0`).
Breaking changes require a major bump and migration notes here.
