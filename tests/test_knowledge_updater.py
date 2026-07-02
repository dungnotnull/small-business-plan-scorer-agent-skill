"""Unit tests for the knowledge updater (Scenario contract 12-13)."""

from __future__ import annotations

import datetime as dt
import textwrap

import knowledge_updater as ku

# -- fixtures ----------------------------------------------------------------

HTML_SAMPLE = textwrap.dedent("""
    <html><head><title>SME survival rates 2026 report - strategy</title></head>
    <body>
      <a href="/article/a">Small business market data 2026 overview</a>
      <a href="/article/b">Business model trends for entrepreneurs</a>
      <a href="/article/c">Unrelated short</a>
      <a href="https://example.com/article/d">Unit economics benchmarks by sector</a>
      <a href="/article/a">Small business market data 2026 overview</a>
    </body></html>
""")


class _FakeClient:
    def __init__(
        self, responses: dict[str, str] | None = None, raise_on: set[str] | None = None
    ) -> None:
        self.responses = responses or {}
        self.raise_on = raise_on or set()
        self.calls: list[str] = []

    def get(self, url: str, timeout: int) -> str:
        self.calls.append(url)
        if url in self.raise_on:
            raise OSError("simulated network failure")
        return self.responses.get(url, "")


# -- Scenario 12: dedup idempotency ------------------------------------------


def test_build_block_dedups_existing_hashes():
    source = {"name": "SBA", "url": "https://sba.gov/advocacy"}
    candidates = ku.parse_candidates(HTML_SAMPLE, source, ku.DEFAULT_KEYWORDS)
    assert candidates, "fixture should yield candidates"
    seen = {ku.entry_hash(candidates[0])}  # pre-seed the first candidate
    block = ku.build_block(candidates, dt.date(2026, 7, 2), seen, ku.DEFAULT_KEYWORDS)
    # first candidate already in seen -> excluded
    assert ku.entry_hash(candidates[0]) not in ku.existing_hashes(block)
    # remaining candidates appear (deduped among themselves)
    lines = [ln for ln in block.splitlines() if ln.startswith("- [")]
    assert len(lines) == len({ku.entry_hash(c) for c in candidates}) - 1


def test_build_block_empty_when_all_seen():
    source = {"name": "SBA", "url": "https://sba.gov/advocacy"}
    candidates = ku.parse_candidates(HTML_SAMPLE, source, ku.DEFAULT_KEYWORDS)
    seen = {ku.entry_hash(c) for c in candidates}
    assert ku.build_block(candidates, dt.date(2026, 7, 2), seen, ku.DEFAULT_KEYWORDS) == ""


def test_existing_hashes_parses_marker():
    text = "- [2026-07-02] Title - Src - https://x <!--h:abcd1234abcd-->\n"
    assert ku.existing_hashes(text) == {"abcd1234abcd"}


def test_entry_hash_stable_and_12_chars():
    c = ku.Candidate("t", "s", "u")
    h = ku.entry_hash(c)
    assert len(h) == 12 and h == ku.entry_hash(c)


def test_format_entry_shape():
    c = ku.Candidate("My Title", "SBA", "https://sba.gov/advocacy")
    line = ku.format_entry(c, dt.date(2026, 7, 2))
    assert line.startswith("- [2026-07-02] My Title - SBA - https://sba.gov/advocacy")
    assert line.rstrip().endswith(ku.entry_hash(c) + "-->")


# -- Scenario 13: degraded fetch never raises --------------------------------


def test_degraded_fetch_records_failure_and_continues(tmp_path):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# brain\n", encoding="utf-8")
    cfg = ku.UpdaterConfig(
        sources=(
            {"name": "Failing", "url": "https://failing.example/"},
            {"name": "OK", "url": "https://ok.example/"},
        ),
        brain_path=brain,
        retries=0,
    )
    client = _FakeClient(
        responses={"https://ok.example/": HTML_SAMPLE}, raise_on={"https://failing.example/"}
    )
    result = ku.run(cfg, dry_run=False, client=client)
    assert result["failures"] == [{"source": "Failing", "url": "https://failing.example/"}]
    # OK source contributed; updater did not crash
    assert "https://ok.example/" in brain.read_text(encoding="utf-8")


def test_run_dry_run_does_not_write(tmp_path):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# brain\n", encoding="utf-8")
    cfg = ku.UpdaterConfig(
        sources=({"name": "OK", "url": "https://ok.example/"},),
        brain_path=brain,
    )
    client = _FakeClient(responses={"https://ok.example/": HTML_SAMPLE})
    before = brain.read_text(encoding="utf-8")
    ku.run(cfg, dry_run=True, client=client)
    assert brain.read_text(encoding="utf-8") == before  # unchanged


# -- parsing unit tests ------------------------------------------------------


def test_parse_candidates_keyword_filter():
    source = {"name": "SBA", "url": "https://sba.gov/advocacy"}
    html = '<a href="/x">Lorem ipsum dolor sit amet consectetur</a>'  # no keyword
    assert ku.parse_candidates(html, source, ku.DEFAULT_KEYWORDS) == []


def test_parse_candidates_length_bounds():
    source = {"name": "SBA", "url": "https://sba.gov/advocacy"}
    too_short = '<a href="/x">SME</a>'  # < MIN_TITLE_LEN
    ok = '<a href="/y">SME survival rates 2026</a>'
    html = too_short + ok
    cands = ku.parse_candidates(html, source, ku.DEFAULT_KEYWORDS)
    assert len(cands) == 1 and cands[0].title == "SME survival rates 2026"


def test_score_candidate_orders_by_keyword_overlap():
    keywords = ("sme", "market", "survival")
    a = ku.Candidate("SME market survival data", "S", "u1")
    b = ku.Candidate("SME data", "S", "u2")
    assert ku.score_candidate(a, keywords) > ku.score_candidate(b, keywords)


def test_config_from_file(tmp_path):
    conf = tmp_path / "conf.json"
    conf.write_text('{"timeout_s": 5, "retries": 1}', encoding="utf-8")
    cfg = ku.UpdaterConfig.from_file(conf)
    assert cfg.timeout_s == 5 and cfg.retries == 1
    # unspecified fields keep defaults
    assert cfg.sources == ku.DEFAULT_SOURCES


def test_main_cli_dry_run(tmp_path, monkeypatch, capsys):
    """CLI must exit 0 and honour --config/--dry-run without touching network."""
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# brain\n", encoding="utf-8")
    conf = tmp_path / "conf.json"
    conf.write_text(
        json_dumps(
            {
                "sources": [{"name": "OK", "url": "https://ok.example/"}],
                "brain_path": str(brain),
            }
        ),
        encoding="utf-8",
    )
    captured = {}

    def _stub_run(cfg, dry_run=False, client=None):
        captured["cfg_brain"] = str(cfg.brain_path)
        captured["dry_run"] = dry_run
        return {"appended": 0, "failures": [], "dry_run": dry_run}

    monkeypatch.setattr(ku, "run", _stub_run)
    rc = ku.main(["--config", str(conf), "--dry-run"])
    assert rc == 0
    assert captured["dry_run"] is True
    assert captured["cfg_brain"] == str(brain)
    out = capsys.readouterr().out
    assert out == ""


def json_dumps(obj):
    import json

    return json.dumps(obj)
