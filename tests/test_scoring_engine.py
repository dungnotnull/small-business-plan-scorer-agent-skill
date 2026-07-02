"""Unit tests for the deterministic feasibility scorer (Scenario contract).

Implements the assertions documented in tests/test-scenarios.md Scenarios
1-3,5,7-11 for `tools/scoring_engine.py`.
"""

from __future__ import annotations

import pytest
import scoring_engine as se

# -- fixtures ----------------------------------------------------------------


def full_canvas() -> dict:
    return {
        "type": "BMC",
        "customer_segments": ["office workers"],
        "value_propositions": ["specialty coffee"],
        "channels": ["walk-in"],
        "customer_relationships": ["loyalty card"],
        "revenue_streams": ["per-cup sales"],
        "key_resources": ["barista", "espresso machine"],
        "key_activities": ["brew", "serve"],
        "key_partnerships": ["local roaster"],
        "cost_structure": ["rent", "beans", "labor"],
    }


def strong_plan(runway: int = 12) -> dict:
    return {
        "canvas": full_canvas(),
        "pricing": {"price_per_unit": 4.5, "currency": "USD"},
        "costs": {"variable_per_unit": 1.5, "cac": 40, "fixed_monthly": 8000},
        "capital": {"cash": 120_000, "monthly_burn": 10_000, "runway_months": runway},
    }


def strong_research(porter_rivalry: int = 3) -> dict:
    return {
        "tam_bottom_up": True,
        "buyers": 12_000,
        "frequency": 3,
        "avg_price": 4.5,
        "som_capture_basis": True,
        "growth_trend_dated": True,
        "porter": {
            "rivalry": porter_rivalry,
            "new_entrants": 3,
            "substitutes": 3,
            "supplier_power": 2,
            "buyer_power": 3,
        },
        "differentiation_gap": False,
    }


def five_assumptions() -> dict:
    return {
        "assumptions": [
            {"name": "demand", "downside_50pct": "halved", "mitigation": "pre-sale"},
            {"name": "price", "downside_50pct": "-15%", "mitigation": "value bundles"},
            {"name": "cac", "downside_50pct": "doubled", "mitigation": "referral"},
            {"name": "margin", "downside_50pct": "-25%", "mitigation": "menu mix"},
            {"name": "runway", "downside_50pct": "1.5x burn", "mitigation": "bridge loan"},
        ]
    }


def _dim(report, name):
    return next(d for d in report.dimensions if d.name == name)


# -- Scenario 1: cafe GO path ------------------------------------------------


def test_scenario1_cafe_go_path():
    report = se.score_plan(strong_plan(), strong_research(), five_assumptions())
    assert report.band == "GO"
    assert report.weighted_total >= 80
    market = _dim(report, "Market opportunity")
    assert market.score == 90 and market.capped is False
    model = _dim(report, "Business-model coherence")
    assert model.score == 90 and model.capped is False


# -- Scenario 2: unknown CAC caps economics ---------------------------------


def test_scenario2_unknown_cac_caps_economics():
    plan = strong_plan()
    plan["costs"]["cac"] = None
    report = se.score_plan(plan, strong_research(), five_assumptions())
    econ = _dim(report, "Unit economics & financials")
    assert econ.score <= 50
    assert econ.capped is True
    assert "CAC" in econ.cap_reason


# -- Scenario 3: loan-ready service scores high economics --------------------


def test_scenario3_loan_ready_high_economics():
    plan = strong_plan(runway=14)
    plan["costs"]["cac"] = 30
    report = se.score_plan(plan, strong_research(), five_assumptions())
    econ = _dim(report, "Unit economics & financials")
    assert econ.score >= 85
    assert report.band == "GO"


# -- Scenario 5: saturated market caps competitive position -----------------


def test_scenario5_saturated_market_low_competitive():
    research = strong_research(porter_rivalry=5)
    research["porter"]["new_entrants"] = 4
    research["porter"]["substitutes"] = 3
    research["porter"]["supplier_power"] = 3
    research["porter"]["buyer_power"] = 4
    report = se.score_plan(strong_plan(), research, five_assumptions())
    comp = _dim(report, "Competitive position")
    assert comp.score <= 54


# -- Scenario 7: top-down TAM caps market -----------------------------------


def test_scenario7_topdown_tam_caps_market():
    research = strong_research()
    research["tam_bottom_up"] = False
    report = se.score_plan(strong_plan(), research, five_assumptions())
    market = _dim(report, "Market opportunity")
    assert market.score <= 40
    assert market.capped is True


# -- Scenario 8: too few assumptions caps risk -------------------------------


def test_scenario8_too_few_assumptions_caps_risk():
    assumptions = {"assumptions": five_assumptions()["assumptions"][:3]}
    report = se.score_plan(strong_plan(), strong_research(), assumptions)
    risk = _dim(report, "Risk & assumptions")
    assert risk.score <= 50
    assert risk.capped is True


# -- Scenario 9: broken BMC links caps model ---------------------------------


def test_scenario9_broken_bmc_links_caps_model():
    plan = strong_plan()
    plan["canvas"]["channels"] = []  # break Revenue->VP->Segment->Channel
    report = se.score_plan(plan, strong_research(), five_assumptions())
    model = _dim(report, "Business-model coherence")
    assert model.score <= 50
    assert model.capped is True


# -- Scenario 10: negative contribution margin floors economics --------------


def test_scenario10_negative_contribution_margin():
    plan = strong_plan()
    plan["pricing"]["price_per_unit"] = 3.0
    plan["costs"]["variable_per_unit"] = 4.0
    report = se.score_plan(plan, strong_research(), five_assumptions())
    econ = _dim(report, "Unit economics & financials")
    assert econ.score == 15


# -- Scenario 11: determinism ------------------------------------------------


def test_scenario11_determinism():
    a = se.score_plan(strong_plan(), strong_research(), five_assumptions())
    b = se.score_plan(strong_plan(), strong_research(), five_assumptions())
    assert a.to_dict() == b.to_dict()


# -- band mapping sanity -----------------------------------------------------


@pytest.mark.parametrize(
    "total,expected",
    [
        (100, "GO"),
        (80, "GO"),
        (79, "CONDITIONAL_GO"),
        (65, "CONDITIONAL_GO"),
        (64, "PIVOT"),
        (50, "PIVOT"),
        (49, "NO_GO"),
        (0, "NO_GO"),
    ],
)
def test_band_mapping(total, expected):
    assert se.band_for(total) == expected


def test_band_out_of_range_raises():
    with pytest.raises(ValueError):
        se.band_for(101)


# -- weights sum to 1 --------------------------------------------------------


def test_weights_sum_to_one():
    total = sum(d["weight"] for d in se.DIMENSIONS)
    assert abs(total - 1.0) < 1e-9
