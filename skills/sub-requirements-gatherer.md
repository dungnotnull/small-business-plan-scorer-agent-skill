---
name: sub-requirements-gatherer
description: Capture the business idea, model, target market, resources, and financial basics into a validated plan object before scoring.
---

## Purpose
Assemble a complete, validated **plan object** that downstream sub-skills
(`sub-scoring-engine`, `sub-quality-reviewer`, `sub-improvement-roadmap`) can
score deterministically. This sub-skill owns the data contract; it must block
forward progress until the minimum viable plan is present.

## Inputs
A free-form user description plus any provided documents. Extract, do not invent:
1. **Business idea** — one-sentence problem→solution.
2. **Model** — Business Model Canvas (9 blocks) OR Lean Canvas (9 blocks).
3. **Target market / segment** — named segment + geography.
4. **Resources** — capital, runway, team (named roles), key assets.
5. **Pricing & costs** — price per unit, variable cost per unit, fixed costs, CAC (if known).
6. **Goals** — planning horizon, target outcome (launch / loan / raise / validate).

## Process
1. **Parse** the user input into the plan-object schema (§Outputs). Mark every
   field `provided`, `inferred` (with basis), or `missing`.
2. **Fill the BMC/Lean Canvas** from inputs; never fabricate blocks. If a block
   is unstated, leave it empty and record it in `gaps`.
3. **Crisp segment & value proposition.** Reject vague segments ("everyone") and
   vague VP ("great quality"). Require a problem→solution pair per segment.
4. **Financial basics.** Capture price, variable cost, fixed cost, capital, monthly
   burn. Compute contribution margin and runway if inputs allow. Mark unknown
   metrics (`CAC: missing`) — do not default them.
5. **Gap-block.** If `model` or `target_market` is missing, STOP and ask the user
   precisely what is missing. Do not proceed to research/scoring.
6. **Emit** the validated plan object (JSON) and a short human-readable summary.

## Outputs — Plan Object Schema (JSON)
```json
{
  "business": {"name": "...", "idea": "problem -> solution"},
  "canvas": {
    "type": "BMC|LeanCanvas",
    "customer_segments": [], "value_propositions": [],
    "channels": [], "customer_relationships": [],
    "revenue_streams": [], "key_resources": [],
    "key_activities": [], "key_partnerships": [],
    "cost_structure": []
  },
  "segment": {"name": "...", "geography": "...", "size_basis": "..."},
  "pricing": {"price_per_unit": null, "currency": "USD"},
  "costs": {"variable_per_unit": null, "fixed_monthly": null, "cac": null},
  "capital": {"cash": null, "monthly_burn": null, "runway_months": null},
  "goals": {"horizon_months": null, "outcome": "launch|loan|raise|validate"},
  "gaps": ["..."],
  "field_status": {"field": "provided|inferred|missing"}
}
```

## Quality Gate
- [ ] `canvas.type` set AND `segment.name` + `segment.geography` defined.
- [ ] Every canvas field has a `field_status` entry; no silent fabrication.
- [ ] `gaps` lists every missing required field; forward flow blocked while required gaps exist.
- [ ] Contribution margin and runway computed **only** when both inputs are present.
