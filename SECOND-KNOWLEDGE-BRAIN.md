# SECOND-KNOWLEDGE-BRAIN.md — Small Business Plan Builder & Scorer (Idea 63)

The canonical, versioned knowledge base for the `small-business-plan-scorer` skill.
Grown weekly by `tools/knowledge_updater.py` (deduped by SHA-1 hash). Offline runs
read this file as the primary evidence source and flag data-currency limitations.

> **Version:** 1.0.0  ·  **Maintained by:** `tools/knowledge_updater.py`  ·
> **Update cadence:** weekly cron  ·  **Dedup key:** `<!--h:<sha1[0:12]>-->`

---

## 1. Strategy Frameworks (canonical reference)

### 1.1 Business Model Canvas (Osterwalder, 2010)
Nine interlocking blocks that describe how a venture creates, delivers, and captures value.

| Block | Question to answer | Evidence required |
|-------|--------------------|-------------------|
| Customer Segments | Who are we creating value for? | Named segment + size estimate |
| Value Propositions | What pain/gain do we solve? | Problem→solution pair per segment |
| Channels | How do we reach customers? | Acquire + deliver + support paths |
| Customer Relationships | How do we engage/retain? | Acquisition, retention, upsell tactics |
| Revenue Streams | How do we earn? | Pricing model + per-unit economics |
| Key Resources | What assets are essential? | Physical/IP/human/financial |
| Key Activities | What must we do well? | Production/problem-solving/platform |
| Key Partnerships | Who supplies/distributes? | Strategic alliances, suppliers |
| Cost Structure | What are the major costs? | Fixed vs variable, COGS vs OPEX |

**Coherence test:** every Revenue Stream traces to a Value Proposition → Segment →
Channel triplet. Missing links reduce the *Model coherence* score.

### 1.2 Lean Canvas (Maurya, 2010)
Startup-adapted 9-block variant. Replaces Key Activities/Partners/Resources and
Customer Relationships with: Problem, Solution, Key Metrics, Unfair Advantage,
and Cost/Revenue streams with an explicit *Existing Alternatives* row.

**Use when:** the venture is pre-revenue or pre-product-market fit. BMC otherwise.

### 1.3 SWOT
Internal (Strengths, Weaknesses) × External (Opportunities, Threats). Used for the
*Operational readiness* and *Risk & assumptions* dimensions. Each item must be
concrete and evidence-backed; vague entries ("strong team") are rejected.

### 1.4 Porter's Five Forces (Porter, 1979)
Industry attractiveness scored 1–5 per force (1 = weak force / favorable, 5 = strong
force / unfavorable). The *Competitive position* dimension is the weighted sum.

| Force | High-pressure signals |
|-------|----------------------|
| Rivalry among existing competitors | Many equal players, slow growth, high fixed costs, low switching costs |
| Threat of new entrants | Low capital barriers, weak regulation, no scale economies |
| Threat of substitutes | Cheaper/better alternative outcomes from adjacent markets |
| Bargaining power of suppliers | Few suppliers, high switching cost, input is scarce |
| Bargaining power of buyers | Concentrated buyers, low switching cost, undifferentiated product |

**Composite attractiveness** = average of the five forces (1.0–5.0). Map to the
*Competitive position* rubric (§3.3).

### 1.5 TAM / SAM / SOM (bottom-up)
Top-down "X% of a $Y market" is rejected unless triangulated bottom-up.

- **TAM** — Total Addressable Market: total demand for the outcome, all segments.
- **SAM** — Serviceable Addressable Market: TAM reachable given geography/channel/model.
- **SOM** — Serviceable Obtainable Market: realistic capture in the planning horizon.

**Bottom-up formula:**
```
TAM = number_of_buyers × purchase_frequency × average_price
SAM = TAM × reach_share   (geography + channel + segment fit)
SOM = SAM × capture_rate  (distribution capacity, marketing budget, conversion)
```
Every multiplier must carry a cited basis; uncited multipliers cap the
*Market opportunity* score at 40/100.

### 1.6 Unit Economics
| Metric | Formula | Pass threshold |
|--------|---------|----------------|
| Contribution margin per unit | price − variable cost per unit | > 0 and stated |
| Gross margin % | (revenue − COGS) / revenue | ≥ industry benchmark − 5pp |
| CAC | sales+marketing spend / new customers | known, not "TBD" |
| LTV | contribution margin × retention periods | LTV / CAC ≥ 3 |
| CAC payback (months) | CAC / monthly contribution margin | ≤ 12 |
| Breakeven volume | fixed costs / contribution margin per unit | ≤ SOM in horizon |
| Runway (months) | cash / monthly burn | ≥ 12, or funded to breakeven |

Missing CAC or gross margin caps *Unit economics & financials* at 50/100 until supplied.

---

## 2. Scoring Dimensions (this skill)

| # | Dimension | Weight | Framework(s) | Hard cap rule |
|---|-----------|--------|--------------|---------------|
| 1 | Market opportunity | 20% | TAM/SAM/SOM | Cap 40 if not bottom-up |
| 2 | Business-model coherence | 20% | BMC/Lean Canvas | Cap 50 if revenue↔VP↔segment link broken |
| 3 | Competitive position | 15% | Porter's Five Forces | Cap 50 if any force unscored |
| 4 | Unit economics & financials | 25% | Unit economics | Cap 50 if CAC or margin missing |
| 5 | Operational readiness | 10% | Ops + SWOT | Cap 60 if no team/ops plan |
| 6 | Risk & assumptions | 10% | SWOT + stress-test | Cap 50 if <5 assumptions tested |

**Weighted total** = Σ(dimension_score × weight).  **Feasibility bands:**
- **80–100 → GO** (strong, proceed)
- **65–79 → CONDITIONAL GO** (milestones required)
- **50–64 → PIVOT** (restructure model/market)
- **0–49 → NO-GO** (fundamental gaps)

---

## 3. Scoring Rubrics (0–100 per dimension)

### 3.1 Market opportunity (TAM/SAM/SOM)
| Score | Evidence |
|-------|----------|
| 85–100 | Bottom-up TAM with cited buyers/freq/price; SAM and SOM with capture rationale; growth trend dated within 12 months |
| 70–84 | Bottom-up TAM; SAM/SOM defensible; one multiplier weakly sourced |
| 55–69 | Bottom-up TAM but ≥1 multiplier uncited; SOM asserted |
| 40–54 | Top-down only, triangulated |
| 0–39 | No sizing or pure assertion |

### 3.2 Business-model coherence (BMC/Lean Canvas)
| Score | Evidence |
|-------|----------|
| 85–100 | All 9 blocks complete; every Revenue→VP→Segment→Channel link traced; no internal contradictions |
| 70–84 | All blocks complete; ≤1 link implicit |
| 55–69 | ≤2 blocks missing or weak |
| 40–54 | Core blocks (VP, Segment, Revenue) present but others absent |
| 0–39 | Model undefined or contradictory |

### 3.3 Competitive position (Porter's Five Forces)
Composite attractiveness C = mean(forces), 1.0 (best) – 5.0 (worst).
| Score | C range |
|-------|---------|
| 85–100 | 1.0–1.8 |
| 70–84 | 1.8–2.6 |
| 55–69 | 2.6–3.4 |
| 40–54 | 3.4–4.2 |
| 0–39 | 4.2–5.0 |
If differentiation gap is noted, allow +5 within the band.

### 3.4 Unit economics & financials
| Score | Evidence |
|-------|----------|
| 85–100 | Contribution margin, CAC, LTV, payback, breakeven, runway all known; LTV/CAC≥3; payback≤12mo; runway≥12mo |
| 70–84 | Core metrics known; one secondary metric estimated with basis |
| 55–69 | Price + variable cost known; CAC or LTV estimated |
| 40–54 | Price only; costs asserted |
| 0–39 | No financials, or negative contribution margin |

### 3.5 Operational readiness (Ops/SWOT)
| Score | Evidence |
|-------|----------|
| 85–100 | Named team w/ roles, ops plan, key resources, legal/regulatory status confirmed |
| 70–84 | Team + ops plan; one readiness item pending |
| 55–69 | Founder-only; partial ops plan |
| 40–54 | No team beyond founder; no ops plan |
| 0–39 | No operational specifics |

### 3.6 Risk & assumptions (SWOT/stress-test)
| Score | Evidence |
|-------|----------|
| 85–100 | ≥5 assumptions tested with downside scenarios; mitigation per risk; SWOT evidence-backed |
| 70–84 | ≥5 tested; ≤2 mitigations generic |
| 55–69 | 3–4 assumptions tested |
| 40–54 | 1–2 assumptions tested |
| 0–39 | No stress-test |

---

## 4. Authoritative Data Sources

| Source | URL | Use |
|--------|-----|-----|
| U.S. SBA Office of Advocacy | sba.gov/advocacy | SME survival/employer statistics |
| SBA Business Guide | sba.gov/business-guide | Feasibility + lender expectations |
| SSRN Entrepreneurship collection | ssrn.com | Academic evidence on failure rates |
| U.S. Census Bureau | census.gov | County Business Patterns, NAICS counts |
| Eurostat SME statistics | ec.europa.eu/eurostat | EU SME base rates |
| OECD SME & Entrepreneurship | oecd.org/sme | Cross-country benchmarks |
| Statista | statista.com | Industry market sizes (paid/summary) |
| IBISWorld | ibisworld.com | Industry structure (paid) |
| Strategyzer library | strategyzer.com/library | BMC/Lean Canvas canon |
| Bureau of Labor Statistics | bls.gov | Wage/unit-labor-cost benchmarks |

### 4.1 Reference base rates (cite in reports)
- **SBA:** ~20% of new employers fail in year 1; ~50% fail by year 5 (sba.gov/advocacy,
  "Frequently Asked Questions About Small Business", latest edition).
- **BLS:** establishment survival ~78% at year 1, ~50% at year 5 (bls.gov/entrepreneurship).
- **OECD:** SMEs are ~99% of all firms and ~60–70% of employment in member economies.

> Base rates above are directional; `knowledge_updater.py` refreshes dated figures.

---

## 5. Self-Update Protocol

- **Queries:** `"SME survival <year>"`, `"small business market data"`,
  `"business model trends"`, `"startup feasibility research"`,
  `"unit economics benchmarks <sector>"`.
- **Sources:** SBA, SSRN, Strategyzer, OECD, Eurostat, census bureaus.
- **Frequency:** weekly (cron). Idempotent via hash dedup.
- **Entry format:**
  `- [YYYY-MM-DD] Title — Source — finding — URL <!--h:<sha1[0:12]-->`
- **Dedup:** SHA-1 of `url + title`, first 12 hex chars, stored in `<!--h:...-->`.
- **Offline/degraded:** updater skips unreachable sources, logs warnings, never deletes.

---

## 6. Knowledge Update Log

- [2026-06-18] Seed entry — frameworks documented.
- [2026-06-18] Scoring rubrics v1.0 — six dimensions + feasibility bands.
- [2026-06-18] Base rates — SBA/BLS/OECD directional figures added.
