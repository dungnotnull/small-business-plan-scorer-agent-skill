# PROJECT-detail.md — Small Business Plan Builder & Scorer (Idea 63)

## Executive Summary
A harness that structures and scores a small-business plan against named strategy frameworks, stress-tests its assumptions, and emits an improvement roadmap with a go/no-go feasibility verdict.

## Problem Statement
Small founders lack rigorous market analysis and realistic financials. This skill provides a structured, framework-grounded plan and feasibility score.

## Target Users & Use Cases
- **Café owner:** "Is my cafe plan viable?" → feasibility score + market check.
- **Online seller:** "Validate my e-commerce plan" → unit economics + competition.
- **Service business:** "Score my plan for a loan" → lender-ready structure.

## Harness Architecture
```
/small-business-plan-scorer
  → sub-requirements-gatherer  (idea, model, resources)    [gate: model + market defined]
  → [main] research            (market data/competition)   [gate: cited + dated]
  → sub-scoring-engine         (feasibility score)         [gate: each dim vs framework]
  → sub-quality-reviewer       (assumption stress-test)    [gate: ≥5 assumptions tested]
  → sub-improvement-roadmap    (improvements + go/no-go)   [gate: verdict + effort/impact]
  → [main] synthesize
```

## Full Sub-Skill Catalog
| Sub-skill | Purpose | Inputs | Outputs | Tools | Gate |
|-----------|---------|--------|---------|-------|------|
| sub-requirements-gatherer | Capture plan | idea, model, resources | plan object | Read | Model + market defined |
| sub-scoring-engine | Score feasibility | plan, frameworks | feasibility score | Read | Each dim vs framework |
| sub-quality-reviewer | Stress-test | plan | assumption log | Read | ≥5 assumptions tested |
| sub-improvement-roadmap | Improve + verdict | scores | roadmap + go/no-go | Write | Verdict + effort/impact |

## Skill File Format Specification
Per Claude skill standard; see skills/main.md.

## E2E Execution Flow
1. Gather the business idea, model (BMC/Lean Canvas), target market, resources, and goals. 2. Research market size (TAM/SAM/SOM), competition (Porter's Five Forces), demand signals. 3. Score feasibility: market opportunity, model coherence, unit economics, competitive position, operational readiness, financial viability. 4. Quality reviewer tests ≥5 assumptions (demand, pricing, CAC, margins, runway). 5. Roadmap improves weak areas + gives a go/no-go/pivot verdict. 6. Render.
Error handling: no financials → request basics; unrealistic projections → challenge; offline → use brain + flag.

## SECOND-KNOWLEDGE-BRAIN Integration
Sources: SSRN, SBA/SME data, industry reports. Weekly append.

## Supporting Tools Spec
`knowledge_updater.py`: queries on SME strategy & market data; weekly cron; dedupe by hash.

## Quality Gates
- Each feasibility dimension mapped to a named framework.
- ≥5 assumptions stress-tested.
- Go/no-go verdict with rationale; market data dated; offline flagged.

## Test Scenarios (summary)
1. Café feasibility. 2. E-commerce unit economics. 3. Loan-ready plan. 4. Unrealistic projection (challenge). 5. Saturated market (Porter). (Full set in tests/.)

## Key Design Decisions
1. BMC/Lean Canvas structure. 2. Porter's Five Forces for competition. 3. TAM/SAM/SOM bottom-up. 4. Assumption stress-test mandatory. 5. Explicit go/no-go.
