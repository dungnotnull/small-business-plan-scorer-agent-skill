"""knowledge_updater.py - Weekly knowledge refresh for the Small Business Plan
Builder & Scorer skill (Idea 63).

Crawls SME-strategy / market-data sources, scores candidate titles by keyword
relevance, deduplicates by SHA-1 hash, and appends new entries to
`SECOND-KNOWLEDGE-BRAIN.md`. Designed to be safe, idempotent, and runnable in
degraded mode: unreachable sources are skipped and logged, never raising.

Run:
    python tools/knowledge_updater.py               # live append
    python tools/knowledge_updater.py --dry-run      # print, do not write
    python tools/knowledge_updater.py --config conf.json

Schedule: weekly cron. Dependencies: standard library only; if `requests` is
installed it is preferred for HTTP.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import logging
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any, Protocol

LOG = logging.getLogger("knowledge_updater")

BRAIN = pathlib.Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"

DEFAULT_SOURCES: tuple[dict[str, str], ...] = (
    {"name": "SBA Office of Advocacy", "url": "https://www.sba.gov/advocacy"},
    {"name": "SSRN Entrepreneurship", "url": "https://www.ssrn.com/index.cfm/en/"},
    {"name": "Strategyzer Library", "url": "https://www.strategyzer.com/library"},
    {"name": "OECD SME", "url": "https://www.oecd.org/sme/"},
    {"name": "Eurostat SME", "url": "https://ec.europa.eu/eurostat/web/sme"},
)
DEFAULT_QUERIES: tuple[str, ...] = (
    "SME survival",
    "small business market data",
    "business model trends",
    "startup feasibility",
    "unit economics benchmarks",
)
DEFAULT_KEYWORDS: tuple[str, ...] = (
    "business",
    "sme",
    "market",
    "model",
    "feasibility",
    "revenue",
    "margin",
    "competition",
    "entrepreneur",
    "strategy",
    "cost",
    "survival",
    "startup",
    "canvas",
    "porter",
)
DEFAULT_TIMEOUT_S = 15
DEFAULT_RETRIES = 2
DEFAULT_RETRY_BACKOFF_S = 2.0
DEFAULT_USER_AGENT = "small-business-plan-scorer/1.0 (+knowledge-updater)"
MIN_TITLE_LEN = 20
MAX_TITLE_LEN = 200


class _HttpClient(Protocol):
    def get(self, url: str, timeout: int) -> str: ...


class UrllibClient:
    """Standard-library HTTP client used when `requests` is unavailable."""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT) -> None:
        self._ua = user_agent

    def get(self, url: str, timeout: int) -> str:
        req = urllib.request.Request(url, headers={"User-Agent": self._ua})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (trusted configured URLs)
            data = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            return data.decode(charset, errors="replace")


def _make_client(user_agent: str) -> _HttpClient:
    """Prefer `requests` if installed, otherwise fall back to urllib."""
    try:
        import requests  # type: ignore

        class RequestsClient:
            def __init__(self, ua: str) -> None:
                self._ua = ua

            def get(self, url: str, timeout: int) -> str:
                r = requests.get(url, headers={"User-Agent": self._ua}, timeout=timeout)  # noqa: S113 (timeout set)
                r.raise_for_status()
                return r.text

        return RequestsClient(user_agent)
    except Exception:
        return UrllibClient(user_agent)


@dataclass
class Candidate:
    title: str
    source: str
    url: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class UpdaterConfig:
    sources: tuple[dict[str, str], ...] = DEFAULT_SOURCES
    queries: tuple[str, ...] = DEFAULT_QUERIES
    keywords: tuple[str, ...] = DEFAULT_KEYWORDS
    timeout_s: int = DEFAULT_TIMEOUT_S
    retries: int = DEFAULT_RETRIES
    retry_backoff_s: float = DEFAULT_RETRY_BACKOFF_S
    user_agent: str = DEFAULT_USER_AGENT
    brain_path: pathlib.Path = BRAIN

    @classmethod
    def from_file(cls, path: pathlib.Path) -> UpdaterConfig:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
        return cls(
            sources=tuple(raw.get("sources", DEFAULT_SOURCES)),
            queries=tuple(raw.get("queries", DEFAULT_QUERIES)),
            keywords=tuple(raw.get("keywords", DEFAULT_KEYWORDS)),
            timeout_s=int(raw.get("timeout_s", DEFAULT_TIMEOUT_S)),
            retries=int(raw.get("retries", DEFAULT_RETRIES)),
            retry_backoff_s=float(raw.get("retry_backoff_s", DEFAULT_RETRY_BACKOFF_S)),
            user_agent=raw.get("user_agent", DEFAULT_USER_AGENT),
            brain_path=pathlib.Path(raw.get("brain_path", str(BRAIN))),
        )


# ---------------------------------------------------------------------------
# Fetch + parse.
# ---------------------------------------------------------------------------


def _fetch_with_retry(client: _HttpClient, url: str, cfg: UpdaterConfig) -> str:
    """Fetch a URL with bounded retries; returns empty string on total failure."""
    last_exc: Exception | None = None
    for attempt in range(cfg.retries + 1):
        try:
            return client.get(url, cfg.timeout_s)
        except (urllib.error.URLError, OSError, TimeoutError, ValueError) as exc:
            last_exc = exc
            if attempt < cfg.retries:
                time.sleep(cfg.retry_backoff_s * (attempt + 1))
        except Exception as exc:  # pragma: no cover - defensive
            last_exc = exc
            if attempt < cfg.retries:
                time.sleep(cfg.retry_backoff_s * (attempt + 1))
    LOG.warning("fetch failed for %s after %d attempts: %s", url, cfg.retries + 1, last_exc)
    return ""


_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_LINK_RE = re.compile(
    r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(fragment: str) -> str:
    text = _TAG_RE.sub(" ", fragment)
    return html.unescape(text).strip()


def parse_candidates(
    html_text: str, source: dict[str, str], keywords: tuple[str, str]
) -> list[Candidate]:
    """Extract title-like candidates from an HTML document.

    Pulls the <title> and all <a> link texts, keeps those whose length is within
    bounds and which contain at least one keyword. Deduplicates by (url, title).
    """
    if not html_text:
        return []
    out: list[Candidate] = []
    seen: set[tuple[str, str]] = set()

    m = _TITLE_RE.search(html_text)
    if m:
        title = _strip_html(m.group(1))
        if MIN_TITLE_LEN <= len(title) <= MAX_TITLE_LEN and _matches(title, keywords):
            key = (source["url"], title)
            if key not in seen:
                seen.add(key)
                out.append(Candidate(title=title, source=source["name"], url=source["url"]))

    for href, inner in _LINK_RE.findall(html_text):
        text = _strip_html(inner)
        if not (MIN_TITLE_LEN <= len(text) <= MAX_TITLE_LEN):
            continue
        if not _matches(text, keywords):
            continue
        absolute = urllib.parse.urljoin(source["url"], href)
        key = (absolute, text)
        if key in seen:
            continue
        seen.add(key)
        out.append(Candidate(title=text, source=source["name"], url=absolute))
    return out


def _matches(text: str, keywords: tuple[str, str]) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in keywords)


def score_candidate(c: Candidate, keywords: tuple[str, str]) -> int:
    """Keyword-overlap score; higher is more relevant. Ties break on title length."""
    lowered = c.title.lower()
    return sum(kw in lowered for kw in keywords)


# ---------------------------------------------------------------------------
# Dedup + append.
# ---------------------------------------------------------------------------

_HASH_RE = re.compile(r"<!--h:([0-9a-f]{12})-->")
_ENTRY_HASH_RE = re.compile(r"^- \[(\d{4}-\d{2}-\d{2})\] (.*) <!--h:([0-9a-f]{12})-->$")


def entry_hash(c: Candidate) -> str:
    return hashlib.sha1(f"{c.url}|{c.title}".encode()).hexdigest()[:12]


def existing_hashes(text: str) -> set[str]:
    return set(_HASH_RE.findall(text))


def format_entry(c: Candidate, day: dt.date) -> str:
    return f"- [{day.isoformat()}] {c.title} - {c.source} - {c.url} <!--h:{entry_hash(c)}-->"


def build_block(
    candidates: list[Candidate], day: dt.date, seen: set[str], keywords: tuple[str, str]
) -> str:
    """Return the markdown block to append, deduping against `seen` (mutated)."""
    ranked = sorted(candidates, key=lambda c: (-score_candidate(c, keywords), -len(c.title)))
    lines: list[str] = []
    for c in ranked:
        h = entry_hash(c)
        if h in seen:
            continue
        seen.add(h)
        lines.append(format_entry(c, day))
    if not lines:
        return ""
    return f"\n### Auto-update {day.isoformat()}\n" + "\n".join(lines) + "\n"


def append_block(brain_path: pathlib.Path, block: str) -> None:
    with brain_path.open("a", encoding="utf-8") as fh:
        fh.write(block)


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------


def run(
    cfg: UpdaterConfig, *, dry_run: bool = False, client: _HttpClient | None = None
) -> dict[str, Any]:
    """Run one update cycle. Returns a structured result for tests/observability."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    client = client or _make_client(cfg.user_agent)
    brain_text = cfg.brain_path.read_text(encoding="utf-8") if cfg.brain_path.exists() else ""
    seen = existing_hashes(brain_text)

    collected: list[Candidate] = []
    failures: list[dict[str, str]] = []
    for source in cfg.sources:
        html_text = _fetch_with_retry(client, source["url"], cfg)
        if not html_text:
            failures.append({"source": source["name"], "url": source["url"]})
            continue
        collected.extend(parse_candidates(html_text, source, cfg.keywords))

    day = dt.date.today()
    block = build_block(collected, day, seen, cfg.keywords)
    result = {
        "date": day.isoformat(),
        "candidates_found": len(collected),
        "appended": block.count("\n- [") if block else 0,
        "failures": failures,
        "dry_run": dry_run,
    }
    if not block:
        LOG.info("no new entries; nothing to do.")
        return result
    if dry_run:
        print(block)
        return result
    append_block(cfg.brain_path, block)
    LOG.info("appended %d entries to %s", result["appended"], cfg.brain_path)
    return result


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Weekly knowledge updater (Idea 63).")
    p.add_argument("--dry-run", action="store_true", help="print block; do not write")
    p.add_argument(
        "--config", type=pathlib.Path, default=None, help="path to JSON config overriding defaults"
    )
    p.add_argument(
        "--brain",
        type=pathlib.Path,
        default=None,
        help="override path to SECOND-KNOWLEDGE-BRAIN.md",
    )
    p.add_argument("--verbose", "-v", action="store_true", help="debug logging")
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_argparser().parse_args(argv)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    cfg = UpdaterConfig.from_file(args.config) if args.config else UpdaterConfig()
    if args.brain:
        cfg.brain_path = args.brain
    run(cfg, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
