---
name: sub-quality-reviewer
description: Stress-test the business plan's core assumptions with downside scenarios before any verdict is issued.
---

## Purpose
Expose the assumptions that would sink the business if wrong, and quantify the
downside. The verdict in `sub-improvement-roadmap` is gated on this log: a critical
unmitigated assumption can downgrade GO → CONDITIONAL GO or CONDITIONAL GO → PIVOT.

## Inputs
- Validated **plan object** from `sub-requirements-gatherer`.
- **Score object** from `sub-scoring-engine` (to weight which assumptions matter).

## Process
1. **Enumerate the mandatory assumption set** (at minimum these five; add
   sector-specific ones as needed):
   1. **Demand size** — SOM volume realistically obtainable in the horizon.
   2. **Willingness-to-pay / pricing** — price the target segment will actually pay.
   3. **Customer acquisition cost (CAC)** — blended CAC achievable at this scale.
   4. **Gross / contribution margin** — unit economics hold at realistic volume.
   5. **Runway / burn** — cash survives to breakeven (or to next funding event).
   Plus, where relevant: **regulatory/licensing**, **supplier dependence**,
   **key-person risk**, **seasonality**.
2. **For each assumption**, answer explicitly:
   - *Basis:* what evidence supports this number? (cite or mark "no basis")
   - *Downside:* recompute the metric at **50% worse** (demand halved, CAC doubled,
     margin compressed 25%, runway consumed 1.5× faster).
   - *Effect:* does the downside push breakeven past the horizon, make contribution
     margin negative, or exhaust runway? Mark `critical: true` if so.
3. **Flag every figure with no basis** — these cap the *Risk & assumptions* dimension
   at 50/100 (per SECOND-KNOWLEDGE-BRAIN.md §2).
4. **Recompute breakeven under the combined worst-case** (all five at 50%-worse
   simultaneously) and report the survival outcome.
5. **Emit** the assumption log (JSON) + sensitivity notes.

## Outputs — Assumption Log Schema (JSON)
```json
{
  "assumptions": [
    {
      "name": "Demand size",
      "stated_value": "...",
      "basis": "cite | no basis",
      "downside_50pct": "...",
      "downside_effect": "...",
      "critical": false,
      "mitigation": "..." 
    }
  ],
  "combined_worst_case": {
    "breakeven_months": null,
    "runway_months": null,
    "survives": true
  }
}
```

## Human-Readable Log
| Assumption | Stated | Basis | 50%-worse downside | Critical? | Mitigation |
|------------|--------|-------|--------------------|-----------|------------|

## Quality Gate
- [ ] **≥5 assumptions tested**, each with a downside scenario.
- [ ] Every assumption has an explicit `basis` ("no basis" is valid but caps risk score).
- [ ] Critical assumptions flagged and fed to `sub-improvement-roadmap`.
- [ ] Combined worst-case breakeven/runway computed and `survives` stated.
