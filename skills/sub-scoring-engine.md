---
name: sub-scoring-engine
description: Score business-plan feasibility across six framework-mapped dimensions and emit a weighted total, feasibility band, and per-dimension rationale.
---

## Purpose
Produce a defensible, reproducible feasibility score grounded in named frameworks.
The engine is deterministic given inputs: same plan + same evidence → same score.
Use `tools/scoring_engine.py` as the reference implementation for the math; this
sub-skill supplies the qualitative judgement and evidence citations.

## Inputs
- Validated **plan object** from `sub-requirements-gatherer`.
- **Market research** (TAM/SAM/SOM figures + Porter scores) — cited and dated.
- **SECOND-KNOWLEDGE-BRAIN.md** rubrics (§3) and hard-cap rules (§2).

## Dimensions, Weights & Frameworks
| # | Dimension | Weight | Framework | Hard cap |
|---|-----------|--------|-----------|----------|
| 1 | Market opportunity | 20% | TAM/SAM/SOM | Cap 40 if not bottom-up |
| 2 | Business-model coherence | 20% | BMC/Lean Canvas | Cap 50 if revenue↔VP↔segment link broken |
| 3 | Competitive position | 15% | Porter's Five Forces | Cap 50 if any force unscored |
| 4 | Unit economics & financials | 25% | Unit economics | Cap 50 if CAC or margin missing |
| 5 | Operational readiness | 10% | Ops + SWOT | Cap 60 if no team/ops plan |
| 6 | Risk & assumptions | 10% | SWOT + stress-test | Cap 50 if <5 assumptions tested |

## Process
1. **Score each dimension 0–100** against the rubric in SECOND-KNOWLEDGE-BRAIN.md §3.
   Pick the band whose evidence criteria the plan meets; score within the band
   by strength of evidence (more/fresher citations → higher).
2. **Apply hard caps.** If a cap rule triggers, clamp the dimension score before
   weighting. Record the cap reason in `rationale`.
3. **Require bottom-up TAM** and realistic margins/CAC. Penalize hand-wavy figures
   by dropping to the band floor.
4. **Compute the weighted total** = Σ(score × weight). Round to the nearest integer.
5. **Map to a feasibility band** (GO ≥80, CONDITIONAL GO 65–79, PIVOT 50–64,
   NO-GO <50).
6. **Emit** the score object (JSON) and a human-readable dimension table.

## Outputs — Score Object Schema (JSON)
```json
{
  "weighted_total": 0,
  "band": "GO|CONDITIONAL_GO|PIVOT|NO_GO",
  "dimensions": [
    {
      "name": "Market opportunity", "weight": 0.20,
      "score": 0, "framework": "TAM/SAM/SOM",
      "capped": false, "cap_reason": null,
      "rationale": "...", "evidence": ["..."]
    }
  ]
}
```

## Human-Readable Dimension Table
| Dimension | Score | Weight | Framework | Capped? | Rationale |
|-----------|-------|--------|-----------|---------|-----------|

## Quality Gate
- [ ] Every dimension has a score, a named framework, and ≥1 evidence pointer.
- [ ] Hard caps applied and `capped`/`cap_reason` populated where triggered.
- [ ] Market sizing is bottom-up (else cap recorded).
- [ ] Weighted total + band computed and stated.
- [ ] Scores reproducible: identical inputs yield identical scores.
