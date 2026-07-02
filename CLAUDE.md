# CLAUDE.md — Small Business Plan Builder & Scorer Skill (Idea 63)

**Skill name:** `small-business-plan-scorer`
**Tagline:** Feasibility-scored business plans for SMEs & sole traders, grounded in strategy frameworks.
**Current phase:** Production-grade complete (Phases 0–5, 100%). 31 unit tests passing.
**Source idea:** 63 — *Build & evaluate a business plan for small businesses/sole traders, score feasibility and analyze the market, grounded in world-renowned business-strategy methods, with improvement recommendations; continuously crawl papers/docs to stay current.*
**Cluster:** `business-operations`

## Problem This Skill Solves
Small founders write optimistic plans with weak market analysis and unrealistic finances. This skill structures the plan with named frameworks (Business Model Canvas, SWOT, Porter's Five Forces, TAM/SAM/SOM, unit economics), scores feasibility, and emits an improvement roadmap.

## Harness Flow Summary
1. **Requirements** (`sub-requirements-gatherer`) — idea, market, model, resources, goals.
2. **Research** (main) — verify market data/competition vs SECOND-KNOWLEDGE-BRAIN.md.
3. **Scoring** (`sub-scoring-engine`) — feasibility score across dimensions.
4. **Challenge** (`sub-quality-reviewer`) — stress-test assumptions.
5. **Roadmap** (`sub-improvement-roadmap`) — plan improvements + go/no-go.

## Sub-skills
- `sub-requirements-gatherer.md` · `sub-scoring-engine.md` · `sub-quality-reviewer.md` · `sub-improvement-roadmap.md`

## Tools Required
WebSearch, WebFetch, Read, Write, Bash.

## Knowledge Sources
SSRN entrepreneurship, SBA/government SME data, industry reports, Osterwalder/Porter literature, census/market-size sources.

## Supporting Python Tools
`tools/knowledge_updater.py` — crawl → SECOND-KNOWLEDGE-BRAIN.md.

## Active Development Tasks
- [x] Scaffold deliverables.
- [x] Phases 0–5 production-grade (frameworks, sub-skills, harness, knowledge pipeline, tests, cross-skill contracts).
- [x] Deterministic scorer 	ools/scoring_engine.py + weekly 	ools/knowledge_updater.py.
- [x] 31 unit tests passing (pytest -q).
- [x] Open-source packaging (pyproject, README, LICENSE, examples).
- [ ] Add sector cost-structure templates (future enhancement, out of phases 0–5).

## Reference Docs
PROJECT-detail.md · PROJECT-DEVELOPMENT-PHASE-TRACKING.md · SECOND-KNOWLEDGE-BRAIN.md
