# Small Business Plan Builder & Scorer

> Feasibility-scored business plans for SMEs & sole traders, grounded in
> world-renowned strategy frameworks — Business Model Canvas, Porter's Five
> Forces, TAM/SAM/SOM, SWOT, and unit economics — with an improvement roadmap
> and an explicit go / conditional-go / pivot / no-go verdict.

This repository ships **two layers**:

1. A **Claude Skill** (`skills/*.md`) — the LLM harness that gathers the plan,
   researches the market, scores feasibility, stress-tests assumptions, and
   produces the roadmap. Designed for a Claude agent with WebSearch/WebFetch/Read/Write/Bash.
2. **Deterministic Python tooling** (`tools/`) — a reference implementation of
   the scorer and a weekly knowledge updater, fully unit-tested, so the scoring
   math is auditable and reproducible independent of the LLM.

---

## What it does

```
sub-requirements-gatherer  -> plan object            [gate: model + market defined]
[main] research            -> market data/competition [gate: cited + dated]
sub-scoring-engine         -> feasibility score       [gate: each dim vs framework]
sub-quality-reviewer       -> assumption stress-test  [gate: >=5 assumptions tested]
sub-improvement-roadmap    -> improvements + verdict  [gate: verdict + effort/impact]
[main] synthesize          -> report
```

**Feasibility dimensions (weighted, framework-mapped):**

| Dimension | Weight | Framework |
|-----------|--------|-----------|
| Market opportunity | 20% | TAM/SAM/SOM |
| Business-model coherence | 20% | BMC / Lean Canvas |
| Competitive position | 15% | Porter's Five Forces |
| Unit economics & financials | 25% | Unit economics |
| Operational readiness | 10% | Ops + SWOT |
| Risk & assumptions | 10% | SWOT + stress-test |

Bands: **GO ≥80**, **CONDITIONAL GO 65–79**, **PIVOT 50–64**, **NO-GO <50**.

---

## Repository layout

```
skills/                 # Claude skill + 4 sub-skills (the harness)
  main.md               # orchestrator + quality gates
  sub-requirements-gatherer.md
  sub-scoring-engine.md
  sub-quality-reviewer.md
  sub-improvement-roadmap.md
tools/                  # deterministic, production-grade Python
  scoring_engine.py     # reference feasibility scorer (CLI + library)
  knowledge_updater.py  # weekly knowledge-brain refresh (CLI + library)
  __init__.py
tests/                  # 31 unit tests + human-readable scenario contract
  test-scenarios.md     # 13 scenarios (the behavioural contract)
  test_scoring_engine.py
  test_knowledge_updater.py
  conftest.py
SECOND-KNOWLEDGE-BRAIN.md   # versioned framework knowledge base
CROSS-SKILL-CONTRACTS.md    # shared plan/score/roadmap schemas for sibling skills
PROJECT-detail.md           # design spec
PROJECT-DEVELOPMENT-PHASE-TRACKING.md
CLAUDE.md
```

---

## Quick start

### Run the deterministic scorer
```bash
python tools/scoring_engine.py plan.json \
    --research research.json --assumptions assumptions.json --out score.json
```
Example input files live implicitly in `tests/test_scoring_engine.py` fixtures.
A minimal plan object:
```json
{
  "canvas": {
    "type": "BMC",
    "customer_segments": ["office workers"],
    "value_propositions": ["specialty coffee"],
    "channels": ["walk-in"],
    "customer_relationships": ["loyalty"],
    "revenue_streams": ["per-cup sales"],
    "key_resources": ["barista"],
    "key_activities": ["brew"],
    "key_partnerships": ["roaster"],
    "cost_structure": ["rent"]
  },
  "pricing": {"price_per_unit": 4.5, "currency": "USD"},
  "costs": {"variable_per_unit": 1.5, "cac": 40, "fixed_monthly": 8000},
  "capital": {"cash": 120000, "monthly_burn": 10000, "runway_months": 12}
}
```

### Refresh the knowledge brain (weekly)
```bash
python tools/knowledge_updater.py --dry-run    # preview
python tools/knowledge_updater.py              # append to SECOND-KNOWLEDGE-BRAIN.md
```
The updater is stdlib-only; if `requests` is installed it is preferred. It degrades
gracefully on network failure (logs + skips, never raises) and deduplicates by SHA-1.

### Run the test suite
```bash
pip install -e ".[dev]"
pytest -q
```
31 tests cover scoring caps, bands, determinism, updater dedup, degraded fetch, and CLI.

---

## Install as a package
```bash
pip install -e .
# optional HTTP client for the updater:
pip install -e ".[http]"
```
Provides console scripts:
- `sbps-score` — feasibility scorer
- `sbps-knowledge-update` — knowledge brain refresh

Library use:
```python
from small_business_plan_scorer.scoring_engine import score_plan
report = score_plan(plan, research, assumptions)
print(report.weighted_total, report.band)
```

---

## Using the Claude Skill
Point a Claude agent at `skills/main.md`. The agent follows the six-stage harness,
invoking the four sub-skills and enforcing the five quality gates (G1–G5). Offline
runs fall back to `SECOND-KNOWLEDGE-BRAIN.md` and flag `Data currency: offline`.
See `skills/main.md` for the full output format and error-handling matrix.

---

## Cross-skill reuse
`CROSS-SKILL-CONTRACTS.md` documents the stable JSON contracts (plan, score,
assumption log, roadmap) reused by sibling skills 57, 67, 76, 78, 107, 144.

---

## License
MIT — see [LICENSE](LICENSE).
