# `baseball-predictions` — SportsData MCP Review

## Fit

This repo already uses MLB Stats API, PyBaseball/Statcast-oriented sources, Retrosheet, ESPN odds and a multi-book odds feed. The reference MCP adds value mainly by **centralizing the official MLB surface and making market/source fallback systematic**.

Keep PyBaseball/Statcast and Retrosheet. They are deeper historical/pitch-level sources than the MCP's role here.

## Recommended groups

```text
mlb.reference
mlb.schedule
mlb.game
mlb.stats
mlb.extra
espn.*
pinnacle.sports
theoddsapi.*
sportsgameodds.*   # if expanding Pick 6/player props
```

## P0: wrap official MLB access behind one adapter

```python
# src/providers/mlb_gateway.py
from dataclasses import dataclass

@dataclass(frozen=True)
class MLBProviderConfig:
    groups: str = "mlb.reference,mlb.schedule,mlb.game,mlb.stats"
    primary: str = "native"
    fallback: str = "sportsdata"


class MLBDataProvider:
    def __init__(self, native, sportsdata):
        self.native = native
        self.sportsdata = sportsdata

    async def schedule(self, date: str):
        try:
            rows = await self.native.schedule(date)
            if rows:
                return rows, "native_mlb"
        except Exception:
            pass
        return await self.sportsdata.call("mlb_schedule", date=date), "sportsdata_mlb"
```

The precise tool argument names should be discovered/pinned in a fixture test. The important design is that callers receive `(payload, source)` and never silently lose provenance.

## P0: event/provider identity

Persist IDs for:

```text
canonical_game_id
mlb_game_pk
espn_event_id
odds_provider_event_id
home_team_id
away_team_id
scheduled_start_utc
```

Use MLB `gamePk` as the preferred canonical id when available.

## P1: official data you can exploit more consistently

The MCP's MLB surface includes schedule, live feed, boxscore, play-by-play, win probability, standings, transactions, rosters and player stats. Useful additions:

- transaction/roster changes as a pregame availability signal;
- confirmed starter changes;
- bullpen recent usage from game logs;
- official venue ids to stabilize park-factor joins;
- live feed/play-by-play validation against existing datasets;
- official win-probability series as an analysis benchmark, not a pregame feature.

### Bullpen workload helper

```python
import pandas as pd


def bullpen_workload(pitcher_games: pd.DataFrame, cutoff, days=3):
    x = pitcher_games.copy()
    x["game_date"] = pd.to_datetime(x["game_date"], utc=True)
    cutoff = pd.Timestamp(cutoff)
    recent = x[(x.game_date < cutoff) & (x.game_date >= cutoff - pd.Timedelta(days=days))]
    return recent.groupby("team_id").agg(
        bullpen_ip=("innings_pitched", "sum"),
        bullpen_pitches=("pitches", "sum"),
        relievers_used=("pitcher_id", "nunique"),
    )
```

## P1: market consensus instead of a single ESPN quote

Your daily recommendation layer should keep ESPN as one observation, not the market.

```python
MARKET_FEATURES = [
    "ml_consensus_home_prob",
    "ml_book_dispersion",
    "runline_consensus",
    "total_consensus",
    "total_dispersion",
    "best_home_price",
    "best_away_price",
    "quote_age_seconds",
]
```

Store raw quotes before computing these fields.

## P1: player props/Pick 6

`sportsgameodds` can be valuable if it provides the required MLB markets in your account because it emphasizes stable market ids across books/time. Use a canonical prop id:

```python
def prop_id(game_pk, player_id, stat, side, line):
    return f"mlb:{game_pk}:{player_id}:{stat}:{side}:{line:g}"
```

Do not train on today's line; use it only for market comparison unless you have historical point-in-time lines.

## P2: source disagreement dashboard

Add a Data Health panel:

```text
MLB schedule       OK   14 games
ESPN schedule      OK   14 games
Matched            14/14
Odds providers     5/6 healthy
Starter conflicts  1
Stale quotes        2
```

This is especially useful in baseball because starters/lineups can change late.

## Tests

```python
def test_game_pk_is_stable_primary_key(): ...
def test_provider_failure_does_not_clear_existing_schedule(): ...
def test_odds_feature_uses_quote_before_prediction_time(): ...
def test_probable_pitcher_change_invalidates_prediction_cache(): ...
def test_venue_mapping_one_to_one(): ...
```

## Bottom line

The strongest improvement is reliability: one official MLB gateway, stable IDs, late-breaking roster/starter validation, and a true multi-book market layer. Keep the existing pitch-level research sources intact.
