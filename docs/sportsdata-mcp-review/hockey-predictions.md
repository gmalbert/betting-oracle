# `hockey-predictions` — SportsData MCP Review

## Fit

The app already consumes the official NHL web/stats APIs plus ESPN odds. `sportsdata-mcp` wraps the current official NHL surface and ESPN, so the primary benefit is **one tested fallback/provenance layer** plus broader market snapshots.

## Recommended groups

```text
nhl.reference
nhl.schedule
nhl.game
nhl.stats
espn.*
theoddsapi.*
oddsapiio.*
```

## P0: source broker

```python
class NHLSourceBroker:
    def __init__(self, native, sportsdata):
        self.native = native
        self.sportsdata = sportsdata

    async def standings(self):
        for source in (self.native, self.sportsdata):
            try:
                data = await source.standings()
                if data:
                    return data, source.name
            except Exception:
                continue
        raise RuntimeError("all NHL standings providers failed")
```

Do not translate “all providers failed” into an empty standings table.

## P1: goalie state should invalidate predictions

Create a prediction dependency hash:

```python
import hashlib


def goalie_state_hash(home_goalie, away_goalie, observed_at):
    raw = f"{home_goalie}|{away_goalie}|{observed_at.isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

When a confirmed starter changes, invalidate/rebuild affected game predictions.

## P1: market consensus + sharp-action research

Store moneyline, puck line and totals per book. Derived fields:

```text
home_ml_no_vig_median
away_ml_no_vig_median
puck_line_consensus
total_consensus
book_dispersion
open_to_current_move
best_price
quote_age
```

Then test whether existing “sharp action” labels actually predict later consensus/closing movement instead of deriving sharpness from one feed.

```python
def steam_signal(open_prob, current_prob, minutes):
    if minutes <= 0:
        return 0.0
    return (current_prob - open_prob) / minutes
```

## P1: official-vs-analytics reconciliation

Your custom xG/goalie analytics should remain model inputs. Use official NHL data for integrity checks:

```text
schedule count
final score
TOI
shots/goals
roster
player ids
standings
```

Write discrepancies to `data_files/provider_discrepancies.parquet` rather than silently overwriting.

## P2: player props

If prop coverage is available from a keyed generic odds provider, start with shots-on-goal because the official NHL data provides natural historical settlement/features.

```python
PROP_KEY = "nhl:{game_id}:{player_id}:shots_on_goal:{line}"
```

Collect lines prospectively before training any line-aware model.

## Tests

```python
def test_goalie_change_invalidates_cache(): ...
def test_nhl_season_id_format_preserved(): ...
def test_provider_error_not_empty_schedule(): ...
def test_market_move_uses_same_book_market_and_line(): ...
```

## Bottom line

Use MCP to harden the existing NHL data layer and establish a real multi-book market ledger. The app's hockey-specific analytics remain the differentiator.
