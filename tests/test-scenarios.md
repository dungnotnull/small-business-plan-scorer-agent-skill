# Test Scenarios — Small Business Plan Builder & Scorer (Idea 63)

These scenarios validate the full harness (`main.md` + four sub-skills) and the
deterministic reference scorer (`tools/scoring_engine.py`). Each scenario states
the input, the expected behaviour, the gates that must pass, and the assertion.
Automated Python assertions live in `tests/test_scoring_engine.py` and
`tests/test_knowledge_updater.py`; this file is the human-readable contract.

---

## Scenario 1 — Cafe feasibility (baseline GO path)
- **Input:** neighbourhood cafe, $80k capital, 60-seat space, full BMC, bottom-up
  TAM, price $4.50 / variable $1.50, CAC known, runway 12+ months, 5 assumptions
  tested with mitigations.
- **Expected:** all six dimensions scored; market bottom-up (no cap); model coherent
  (no cap); weighted total in GO band (≥80); verdict GO.
- **Gates:** G1 model+market, G2 sourced+dated, G3 frameworks mapped, G4 ≥5
  assumptions, G5 verdict + rationale.
- **Pass:** `band_for(total) == "GO"`; no dimension `capped` for cafe-class plan.

## Scenario 2 — E-commerce with unknown CAC (cap triggers)
- **Input:** dropshipping plan, full BMC, bottom-up TAM, price/cost known,
  **CAC missing**, 5 assumptions tested.
- **Expected:** *Unit economics & financials* capped at 50 (`cac missing`); score
  object records `capped=True` with `cap_reason` mentioning CAC.
- **Pass:** economics dimension `score <= 50` and `capped == True`.

## Scenario 3 — Loan-ready service business (financial rigour)
- **Input:** service business seeking a bank loan; realistic financials, CAC, LTV,
  payback, runway ≥ 12 months.
- **Expected:** economics dimension high (≥85 when all metrics + runway≥12);
  verdict references repayment capacity (runway/breakeven).
- **Pass:** economics `score >= 85`; verdict rationale cites runway/breakeven.

## Scenario 4 — Unrealistic projection (challenge downgrades verdict)
- **Input:** plan projecting 300% YoY growth with no basis; 5 assumptions but the
  demand assumption has `"basis": "no basis"` and a 50%-worse downside that exhausts
  runway → `critical: true`, unmitigated.
- **Expected:** *Risk & assumptions* not penalised by count (5 tested) but
  `sub-improvement-roadmap` downgrades from GO to PIVOT because a critical
  assumption is unmitigated.
- **Pass:** roadmap verdict == PIVOT; rationale cites the critical assumption.

## Scenario 5 — Saturated market (Porter penalises competitive position)
- **Input:** bubble-tea shop on a street with five competitors; Porter composite
  ~4.0 (rivalry 5, new entrants 4, substitutes 3, supplier power 3, buyer power 4).
- **Expected:** *Competitive position* scores in the 40-54 band (composite 3.4-4.2);
  roadmap suggests a differentiation pivot.
- **Pass:** competitive `score <= 54`; verdict PIVOT with differentiation gap noted.

## Scenario 6 — Offline / degraded mode
- **Input:** any plan with WebSearch unavailable.
- **Expected:** harness falls back to `SECOND-KNOWLEDGE-BRAIN.md`, sets
  `data_currency: offline`, and caps market claims lacking ≤12-month citations.
- **Pass:** report contains `Data currency: offline`; G2 passes via offline flag.

## Scenario 7 — Top-down TAM (market cap)
- **Input:** plan with `research.tam_bottom_up = false`.
- **Expected:** *Market opportunity* capped at 40 with cap reason referencing
  bottom-up TAM.
- **Pass:** market `score <= 40` and `capped == True`.

## Scenario 8 — Too few assumptions (risk cap)
- **Input:** only 3 assumptions tested.
- **Expected:** *Risk & assumptions* capped at 50; G4 fails (must ask for ≥5).
- **Pass:** risk `score <= 50` and `capped == True`; harness blocks at G4.

## Scenario 9 — Broken BMC links (model cap)
- **Input:** BMC missing `channels` (Revenue↔VP↔Segment↔Channel link broken).
- **Expected:** *Business-model coherence* capped at 50.
- **Pass:** model `score <= 50` and `capped == True`.

## Scenario 10 — Negative contribution margin (economics floor)
- **Input:** price $3.00, variable cost $4.00.
- **Expected:** *Unit economics & financials* raw score 15 (negative contribution),
  pre-cap; final score 15.
- **Pass:** economics `score == 15`.

## Scenario 11 — Determinism (reproducibility)
- **Input:** identical plan + research + assumptions run twice.
- **Expected:** identical `weighted_total`, `band`, and per-dimension `score`.
- **Pass:** two `score_plan` calls produce equal reports.

## Scenario 12 — Knowledge updater dedup (idempotency)
- **Input:** brain file with an existing entry hash; updater fed the same candidate.
- **Expected:** updater produces zero new entries (block is empty).
- **Pass:** `build_block` returns `""` when the candidate hash is already in `seen`.

## Scenario 13 — Knowledge updater degraded fetch
- **Input:** a source URL that raises on fetch.
- **Expected:** updater logs a warning, records the failure, continues other
  sources, never raises.
- **Pass:** `run` returns with `failures` populated and exit code 0.
