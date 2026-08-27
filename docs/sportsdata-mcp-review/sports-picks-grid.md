# `sports-picks-grid` — SportsData MCP Review

## Biggest improvement: make this the portfolio's normalized read model

Sports Picks Grid correctly contains no models. It should remain that way. Its next evolution is to become the **single normalized serving layer** for recommendations, market freshness, provider health and model performance across every sport repo.

`sportsdata-mcp` does not need to be called directly by the dashboard. Instead, sport repos should use the shared gateway, then export richer standardized artifacts that this repo aggregates.

## P0: replace the hard-coded 13-repo registry with a manifest

Create `config/portfolio.json`:

```json
{
  "schema_version": 2,
  "sports": [
    {
      "id": "mlb",
      "repo": "gmalbert/baseball-predictions",
      "display_name": "Betting Cleanup",
      "picks_path": "data_files/best_bets_today.json",
      "performance_path": "data_files/model_performance.json",
      "health_path": "data_files/provider_health.json",
      "active_months": [3,4,5,6,7,8,9,10]
    }
  ]
}
```

Then adding a new sport is data, not code.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class SportSource:
    id: str
    repo: str
    picks_path: str
    performance_path: str | None = None
    health_path: str | None = None
```

## P0: unified pick schema v2

Standardize every exported recommendation:

```json
{
  "schema_version": 2,
  "sport": "nfl",
  "league": "NFL",
  "event_key": "...",
  "event_start": "2026-09-13T17:00:00Z",
  "generated_at": "2026-09-13T12:00:00Z",
  "market": "spread",
  "selection": "BUF",
  "line": -2.5,
  "price_decimal": 1.91,
  "price_american": -110,
  "model_probability": 0.574,
  "market_fair_probability": 0.524,
  "edge": 0.050,
  "expected_value": 0.096,
  "tier": "strong",
  "model_version": "v2.3",
  "market_snapshot_id": "...",
  "books_observed": 5,
  "quote_age_seconds": 480,
  "data_status": "ready",
  "notes": []
}
```

Do not let each sport redefine what `confidence`, `edge`, or odds format means without metadata.

## P0: validation on ingestion

Use Pydantic so a malformed repo cannot poison the whole dashboard.

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class UnifiedPick(BaseModel):
    schema_version: int = 2
    sport: str
    league: str
    event_key: str
    event_start: datetime
    generated_at: datetime
    market: str
    selection: str
    line: float | None = None
    price_decimal: float = Field(gt=1)
    model_probability: float = Field(ge=0, le=1)
    market_fair_probability: float = Field(ge=0, le=1)
    edge: float
    expected_value: float
    tier: Literal["elite", "strong", "good", "standard", "pass"]
    books_observed: int = Field(ge=0)
    quote_age_seconds: int | None = Field(default=None, ge=0)
    data_status: str
```

Invalid rows go to an error report; they should not crash all sports.

## P1: freshness should be first-class

Current behavior falls back to recent historical picks in the offseason. Preserve that for browsing, but never visually mix a stale historical recommendation with a current actionable pick.

```python
def classify_pick_state(pick, now):
    if pick.event_start < now:
        return "historical"
    age = (now - pick.generated_at).total_seconds()
    if age > 24 * 3600:
        return "stale"
    if pick.data_status != "ready":
        return "degraded"
    return "current"
```

UI badges:

```text
CURRENT
STALE
HISTORICAL
DEGRADED SOURCE
MARKET MISSING
```

## P1: cross-sport ranking based on EV quality, not raw confidence

A 70% favorite probability in MLB is not directly comparable to a 70% prop probability in NFL. Rank using standardized evidence:

```python
score = (
    0.40 * calibrated_edge_score
    + 0.25 * expected_value_score
    + 0.20 * model_reliability_score
    + 0.15 * market_quality_score
)
```

Where market quality includes book count/freshness/dispersion and model reliability is based on **historical out-of-sample calibration**, not the current model's confidence alone.

## P1: provider-health dashboard

Aggregate `provider_health.json` from all repos:

```text
Sport   Model cache   Fixtures   Market   Books   Last refresh
NFL     OK            OK         OK       6       14m
Tennis  OK            OK         DEGRADED 1       2h
Rugby   OK            OK         MISSING  0       —
```

This makes data problems visible before a user interprets a blank card as “no bets.”

## P1: performance contract

Standardize `model_performance.json`:

```json
{
  "sport": "nfl",
  "as_of": "...",
  "evaluation": "walk_forward_oos",
  "bets": 218,
  "wins": 121,
  "losses": 91,
  "pushes": 6,
  "roi": 0.043,
  "clv_mean": 0.011,
  "brier": 0.221,
  "max_drawdown_units": 12.4
}
```

The Grid can then compare models honestly without scraping prose from READMEs.

## P2: use GitHub conditional requests / manifest hashes

The aggregator should not redownload unchanged files.

Store:

```text
repo
path
etag/content sha
last_checked
last_changed
```

Skip processing when content SHA is unchanged.

## P2: optional Betting Oracle MCP surface

Sports Picks Grid is the natural backend for a read-only MCP tool such as:

```text
get_today_picks
get_best_bets
get_sport_health
get_model_performance
```

That lets AI clients query your normalized portfolio rather than each repo separately.

## Tests

```python
def test_one_bad_repo_does_not_break_all_picks(): ...
def test_historical_fallback_not_labeled_current(): ...
def test_cross_sport_rank_uses_calibration_not_raw_confidence(): ...
def test_schema_v1_migrates_or_fails_explicitly(): ...
def test_provider_health_is_visible_for_empty_slate(): ...
```

## Bottom line

Keep this app model-free. Make it the portfolio's **strict, versioned, freshness-aware read model**. That change magnifies every provider and model improvement made in the underlying repos.
