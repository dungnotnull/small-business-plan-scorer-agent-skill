---
name: sub-improvement-roadmap
description: Convert dimension scores and the assumption stress-test into a prioritized improvement roadmap and an explicit go/no-go/pivot verdict with rationale.
---

## Purpose
Turn the diagnosis (scores + assumption log) into a concrete action plan and a
single, defensible decision. The verdict must be traceable to specific scores and
assumptions so a lender or founder can audit it.

## Inputs
- **Score object** from `sub-scoring-engine` (six dimensions + weighted total + band).
- **Assumption stress-test log** from `sub-quality-reviewer`.
- **Plan object** goals (horizon + outcome) from `sub-requirements-gatherer`.

## Process
1. **Rank** the six dimensions by `score` ascending; the lowest three are primary
   targets. Rank assumptions by risk (downside severity) descending.
2. **Pair** each low dimension with its riskiest assumption and produce one concrete
   improvement per pair (not generic advice). Examples that pass:
   - "Validate demand: run a 2-week pre-sale landing page targeting the SOM; pass =
     ≥30 deposits at the stated price." (effort S, impact High)
   - "Reduce CAC: shift 60% of paid spend to referral + content; re-measure CAC at
     week 8; pass = CAC payback ≤ 12 months." (effort M, impact High)
3. **Tag** every improvement: `effort` (S/M/L) and `impact` (Low/Med/High). Effort
   is person-weeks (S ≤2, M 3–8, L >8). Impact is the expected dimension uplift.
4. **Set milestones.** Each Conditional-Go or Pivot improvement carries a measurable
   milestone and a deadline within the planning horizon.
5. **Issue the verdict** using the rules in §Verdict Rules — based on band AND the
   most severe unmitigated assumption, not band alone.
6. **Emit** the roadmap object (JSON) and the human-readable roadmap + verdict.

## Verdict Rules
| Band | Worst unmitigated assumption | Verdict |
|------|------------------------------|---------|
| ≥80 | none critical | **GO** |
| ≥80 | ≥1 critical, mitigated by a milestone | **CONDITIONAL GO** |
| 65–79 | none critical | **CONDITIONAL GO** (milestones required) |
| 65–79 | ≥1 critical, no mitigation | **PIVOT** |
| 50–64 | — | **PIVOT** |
| <50 | — | **NO-GO** |
A critical assumption = one whose 50%-worse downside pushes breakeven or runway
past the planning horizon, or makes contribution margin negative.

## Outputs — Roadmap Object Schema (JSON)
```json
{
  "verdict": "GO|CONDITIONAL_GO|PIVOT|NO_GO",
  "verdict_rationale": "...",
  "improvements": [
    {
      "dimension": "Unit economics & financials",
      "assumption": "...",
      "action": "...",
      "effort": "S|M|L",
      "impact": "Low|Med|High",
      "milestone": "...", "deadline": "YYYY-MM-DD"
    }
  ]
}
```

## Human-Readable Roadmap
| # | Dimension | Action | Effort | Impact | Milestone | Deadline |
|---|-----------|--------|--------|--------|-----------|----------|

## Quality Gate
- [ ] Verdict stated with rationale citing ≥1 score and ≥1 assumption.
- [ ] Every improvement has effort + impact + (if Conditional/Pivot) milestone.
- [ ] No generic advice; each action names a concrete test or change.
- [ ] Verdict consistent with §Verdict Rules (auditable).
