# PROJECT-DEVELOPMENT-PHASE-TRACKING.md — Small Business Plan Builder & Scorer (Idea 63)

> Overall status: **100% complete — all phases 0–5 done. Production-grade, open-source ready.**
> Verified by: `pytest -q` → 31 passed. Package installs (`pip install -e .`) with console
> scripts `sbps-score` and `sbps-knowledge-update`. Example end-to-end run:
> `examples/plan.json` → `examples/score.json` (total 86, GO).

## Phase 0 — Research & Architecture  ✅ 100%
- **Tasks:** catalog frameworks (Business Model Canvas, Lean Canvas, SWOT, Porter's Five
  Forces, TAM/SAM/SOM, unit economics); define feasibility dimensions, weights, hard-cap
  rules, and 0–100 rubrics per dimension.
- **Deliverables:** `SECOND-KNOWLEDGE-BRAIN.md` v1.0.0 — full framework docs with formulas,
  bottom-up TAM/SAM/SOM formula, unit-economics metrics + pass thresholds, Porter scoring,
  six-dimension rubric tables, feasibility bands, base rates (SBA/BLS/OECD), authoritative
  source list, self-update protocol.
- **Success:** ≥4 frameworks documented → **6 frameworks documented** with rubrics.
- **Effort:** S. **Status:** ✅ Done.

## Phase 1 — Core Sub-Skills  ✅ 100%
- **Tasks:** `sub-requirements-gatherer`, `sub-scoring-engine`, `sub-improvement-roadmap`.
- **Deliverables:** three sub-skill files rewritten with explicit JSON schemas, rubric
  references, hard-cap logic, gate criteria, verdict rules, and effort/impact definitions.
  `sub-requirements-gatherer` owns the plan-object contract; `sub-scoring-engine` defines the
  score-object contract; `sub-improvement-roadmap` defines the roadmap-object contract +
  verdict matrix.
- **Success:** plan→score→roadmap flows with schemas → **achieved**.
- **Effort:** M. **Status:** ✅ Done.

## Phase 2 — Main Harness + Quality Gates  ✅ 100%
- **Tasks:** `main.md`; `sub-quality-reviewer` (assumption stress-test).
- **Deliverables:** `skills/main.md` rewritten as a six-stage harness with explicit gates
  G1–G5, error-handling matrix, offline/degraded-mode behaviour, and full output format.
  `sub-quality-reviewer.md` defines the mandatory assumption set (≥5), 50%-worse downside
  protocol, critical-flag rules, combined worst-case breakeven/runway, and the assumption-log
  schema.
- **Success:** E2E ≥5 assumptions tested; gates pass → **achieved**.
- **Effort:** M. **Status:** ✅ Done.

## Phase 3 — Knowledge Pipeline  ✅ 100%
- **Tasks:** `knowledge_updater.py` (SBA/SSRN/OECD/Eurostat/Strategyzer).
- **Deliverables:** `tools/knowledge_updater.py` rewritten production-grade: dataclass config,
  JSON config override, bounded retries with backoff, stdlib HTTP with optional `requests`,
  HTML candidate parsing, keyword relevance scoring, SHA-1 dedup, dry-run, structured run
  result, graceful degradation (never raises on fetch failure), CLI. Plus a deterministic
  reference scorer `tools/scoring_engine.py` implementing the rubric math, hard caps, bands,
  CLI, and library API.
- **Success:** dry-run appends deduped entries → **verified** by
  `tests/test_knowledge_updater.py` (dedup, degraded fetch, CLI, config).
- **Effort:** M. **Status:** ✅ Done.

## Phase 4 — Testing & Validation  ✅ 100%
- **Tasks:** ≥5 scenarios incl. unrealistic projection.
- **Deliverables:** `tests/test-scenarios.md` — 13 human-readable scenarios (the behavioural
  contract). `tests/test_scoring_engine.py` (19 tests: bands, caps, determinism, weights) and
  `tests/test_knowledge_updater.py` (12 tests: dedup, parsing, degraded fetch, CLI, config).
  `tests/conftest.py` shared path setup. Total **31 passing**.
- **Success:** all gated and green → **achieved**.
- **Effort:** S. **Status:** ✅ Done.

## Phase 5 — Cross-Skill Wiring  ✅ 100%
- **Tasks:** share `sub-requirements-gatherer`/`sub-scoring-engine` with 57, 67, 76, 78, 107, 144.
- **Deliverables:** `CROSS-SKILL-CONTRACTS.md` — four versioned JSON contracts (plan, score,
  assumption log, roadmap), reuse map per sibling skill, compatibility rules, and versioning
  policy. Reuse enforced via the deterministic `scoring_engine.score_plan` reference.
- **Success:** shared contracts documented → **achieved**.
- **Effort:** S. **Status:** ✅ Done.

## Open-Source Readiness  ✅ 100%
- `README.md`, `LICENSE` (MIT), `pyproject.toml` (setuptools package `small_business_plan_scorer`
  + console scripts + pytest/ruff config), `requirements.txt`, `requirements-optional.txt`,
  `.gitignore`, `tools/__init__.py`, `examples/{plan,research,assumptions,score}.json`.
- Deterministic scorer and updater are stdlib-first; `requests` optional.
- `pip install -e .` and `pip install -e ".[dev]"` supported; `pytest -q` → 31 passed.

## Verification commands
```bash
pip install -e ".[dev]"
pytest -q                                   # 31 passed
python tools/scoring_engine.py examples/plan.json \
    --research examples/research.json --assumptions examples/assumptions.json --out examples/score.json
python tools/knowledge_updater.py --dry-run
```
