# `college-football-predictions` — SportsData MCP Review

## Why this is one of the best integrations in the portfolio

This repo already has the right modeling discipline: point-in-time features, expanding-season validation, explicit abstention, provider-level market normalization, risk controls, and a 2026 shadow ledger. Its own README identifies the biggest unresolved market-data problem: **historical line movement and CLV cannot be reconstructed without immutable multi-book snapshots that were actually observed before kickoff**.

`sportsdata-mcp` can help fill that exact gap without replacing CFBD.

## Keep as primary

- Native CFBD ingestion and its current canonical schema.
- Existing market/settlement/risk utilities.
- Existing prediction contracts and manifests.
- Existing `scripts/snapshot_market.py` design.

## Add through SportsData MCP

### Highest-value groups/providers

1. `cfbd.*` — use as an alternate transport / endpoint surface, not as a second truth source.
2. `espn.*` — independent fixtures, event ids, scores, rosters/news where available.
3. `ncaa.college` — scoreboard, conference standings, AP/coaches polls.
4. `theoddsapi.*` — multi-book current and historical snapshots when your subscription supports them.
5. `oddsapiio.*` — broad bookmaker coverage.
6. `sportsgameodds.*` — stable market ids and player props if you expand prop modeling.
7. Pinnacle/other sharp-price tools where the event exists and the provider is reachable.

## P0: turn the existing snapshot collector into a multi-provider quote ledger

Do not replace your canonical quote schema. Add an adapter that writes all raw provider quotes into it.

```python
# utils/sportsdata_market_adapter.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass(frozen=True)
class NormalizedQuote:
    game_id: str
    provider: str
    bookmaker: str
    market_type: str
    side: str
    line: float | None
    price_decimal: float | None
    observed_at: datetime
    source_event_id: str | None
    source_market_id: str | None
    raw: dict[str, Any]


def american_to_decimal(price: float | int | None) -> float | None:
    if price is None:
        return None
    p = float(price)
    if p == 0:
        return None
    return 1 + (100 / abs(p) if p < 0 else p / 100)


def normalize_price(value: Any, fmt: str) -> float | None:
    if value in (None, ""):
        return None
    if fmt == "decimal":
        return float(value)
    if fmt == "american":
        return american_to_decimal(float(value))
    raise ValueError(f"unsupported odds format: {fmt}")
```

The provider-specific parser should be deliberately thin:

```python
def parse_provider_quotes(
    *,
    payload: dict,
    game_id: str,
    provider: str,
    observed_at: datetime,
) -> list[NormalizedQuote]:
    """Convert a probed provider response to canonical quotes.

    Keep this function provider-specific. Do not make the training pipeline
    understand the upstream schema.
    """
    rows: list[NormalizedQuote] = []

    for market in payload.get("markets", []):
        for selection in market.get("selections", []):
            rows.append(
                NormalizedQuote(
                    game_id=game_id,
                    provider=provider,
                    bookmaker=str(payload.get("bookmaker", provider)),
                    market_type=str(market.get("type")),
                    side=str(selection.get("name")),
                    line=(
                        float(selection["line"])
                        if selection.get("line") is not None
                        else None
                    ),
                    price_decimal=normalize_price(
                        selection.get("price"),
                        payload.get("odds_format", "decimal"),
                    ),
                    observed_at=observed_at,
                    source_event_id=str(payload.get("event_id", "")) or None,
                    source_market_id=str(market.get("id", "")) or None,
                    raw={"market": market, "selection": selection},
                )
            )
    return rows
```

### Snapshot cadence

For 2026 shadow deployment, capture at multiple horizons:

```text
T-7d      once/day
T-48h     every 6h
T-24h     every 3h
T-6h      hourly
T-90m     every 30m
T-15m     once
```

GitHub Actions cannot run more frequently than every 5 minutes and is not guaranteed exact; an hourly workflow is sufficient for most pregame movement research. A small VPS/cron can handle 30-minute snapshots if desired.

```yaml
name: Market snapshots

on:
  workflow_dispatch:
  schedule:
    - cron: "11 * * * *"

jobs:
  snapshot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pip install "sportsdata-mcp>=0.31,<0.32"
      - name: Snapshot
        env:
          CFBD_API_KEY: ${{ secrets.CFBD_API_KEY }}
          THE_ODDS_API_KEY: ${{ secrets.THE_ODDS_API_KEY }}
          ODDS_API_IO_KEY: ${{ secrets.ODDS_API_IO_KEY }}
          SPORTSDATA_MCP_GROUPS: >-
            espn.*,ncaa.college,theoddsapi.*,oddsapiio.*,cfbd.*
        run: python scripts/snapshot_market_sportsdata.py
```

## P0: preserve disagreement instead of collapsing too early

Create features at the prediction cutoff from all books:

```python
import numpy as np
import pandas as pd


def market_state_features(quotes: pd.DataFrame) -> dict[str, float]:
    """Build robust market-state features from one game/market snapshot."""
    out: dict[str, float] = {}

    for col in ["home_spread", "total"]:
        s = pd.to_numeric(quotes[col], errors="coerce").dropna()
        if s.empty:
            continue
        out[f"{col}_median"] = float(s.median())
        out[f"{col}_mean"] = float(s.mean())
        out[f"{col}_std"] = float(s.std(ddof=0))
        out[f"{col}_range"] = float(s.max() - s.min())
        out[f"{col}_book_count"] = float(s.size)

    return out
```

Add explicit sharp-vs-field measures when Pinnacle or another designated sharp source is present:

```python
def sharp_delta(
    quotes: pd.DataFrame,
    value_col: str,
    sharp_books: set[str] = {"pinnacle"},
) -> float | None:
    x = quotes.dropna(subset=[value_col]).copy()
    sharp = x[x["bookmaker"].str.lower().isin(sharp_books)]
    retail = x[~x["bookmaker"].str.lower().isin(sharp_books)]
    if sharp.empty or retail.empty:
        return None
    return float(sharp[value_col].median() - retail[value_col].median())
```

Useful features:

```text
open_spread_consensus
current_spread_consensus
spread_move
spread_dispersion
sharp_spread_delta
open_total_consensus
current_total_consensus
total_move
total_dispersion
sharp_total_delta
book_count
quote_age_seconds
books_disagreeing_with_consensus_1pt
books_disagreeing_with_consensus_2pt
```

## P1: opening/closing quote contract

Make the cutoff semantics executable:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class MarketCutoffs:
    prediction_time: datetime
    kickoff: datetime

    @property
    def closing_cutoff(self) -> datetime:
        # Avoid accidentally ingesting a quote observed after kickoff because
        # one feed labels the game "pregame" for a few seconds too long.
        return self.kickoff - timedelta(minutes=2)
```

```python
def select_asof_quote(df, cutoff):
    q = df[df["observed_at"] <= cutoff].sort_values("observed_at")
    return q.groupby(
        ["game_id", "bookmaker", "market_type", "side"],
        dropna=False,
    ).tail(1)
```

Your historical model must select with `prediction_time`; settlement/CLV analytics may select with `closing_cutoff`. Never share those dataframes.

## P1: provider triangulation for schedules and game identity

Use CFBD as canonical, ESPN/NCAA only for verification.

Create `data_files/processed/provider_game_map.parquet`:

```text
canonical_game_id
season
week
home_team_id
away_team_id
kickoff_utc
cfbd_game_id
espn_event_id
ncaa_game_id
match_score
verified_at
```

Fuzzy matching should be a one-time reconciliation step, not happen inside model feature generation.

```python
from rapidfuzz.fuzz import ratio


def game_match_score(a_home, a_away, b_home, b_away) -> float:
    direct = (ratio(a_home, b_home) + ratio(a_away, b_away)) / 2
    swapped = (ratio(a_home, b_away) + ratio(a_away, b_home)) / 2
    return max(direct, swapped)
```

Require matching kickoff windows and team aliases before accepting a match.

## P1: NCAA polls as point-in-time features

The NCAA provider can add AP/coaches poll snapshots. Store them by publication date and use only the most recent poll known before kickoff.

Potential features:

```text
home_ap_rank
away_ap_rank
home_coaches_rank
away_coaches_rank
rank_diff
ranked_vs_unranked
both_ranked
poll_disagreement_home
poll_disagreement_away
```

Do not use final-season rankings for earlier games.

## P2: player props only after identity/timestamp infrastructure exists

If you expand into QB/RB/WR props, `sportsgameodds` is interesting because stable market ids make it easier to join a prop across books and over time. Add this only after:

- player identity mapping;
- immutable quotes;
- injury/QB status timestamping;
- snap/usage point-in-time features;
- settlement rules for pushes/voids.

Suggested canonical prop key:

```python
def prop_key(game_id: str, player_id: str, stat: str, period: str = "game") -> str:
    return f"{game_id}:{player_id}:{stat}:{period}"
```

## P2: source-health gate for shadow picks

A model may be valid but the market context may not be.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class MarketReadiness:
    enough_books: bool
    quotes_fresh: bool
    consensus_available: bool
    no_provider_errors: bool

    @property
    def ready(self) -> bool:
        return all((
            self.enough_books,
            self.quotes_fresh,
            self.consensus_available,
            self.no_provider_errors,
        ))
```

The UI should distinguish:

```text
MODEL_ABSTAIN
MARKET_DATA_INSUFFICIENT
MARKET_DATA_STALE
NO_EDGE
SHADOW_SIGNAL
```

## Tests to add

```python
def test_historical_market_feature_never_reads_future_quote(): ...
def test_closing_quote_precedes_kickoff(): ...
def test_consensus_robust_to_one_outlier_book(): ...
def test_provider_failure_is_not_empty_slate(): ...
def test_team_mapping_is_one_to_one_per_provider(): ...
def test_poll_feature_uses_publication_date_before_game(): ...
def test_same_game_provider_ids_do_not_change_after_rebuild(): ...
```

## Expected payoff

This does not promise a new betting edge. It gives the current shadow deployment the missing evidence needed to answer the much more important questions:

- Did a signal beat the line available when it was generated?
- Did the market move toward the model before kickoff?
- Is the apparent total edge independent of one provider?
- Does model performance survive when measured against a multi-book consensus rather than one line?
- Does edge persist after price, vig, and latency are included?

That is the correct next step for this repo.
