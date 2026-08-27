# `darts` — SportsData MCP Review

## Fit

BullzIQ already uses Odds-API.io `/v3` and has explicit request-budget constraints. `sportsdata-mcp` can centralize that odds transport, caching, error handling and provenance, but the reviewed reference catalogue does **not** provide a clearly documented darts-statistics provider. Do not pretend MCP replaces dartsdatabase.co.uk historical data.

## Recommended groups

```text
oddsapiio.*
theoddsapi.*       # if darts coverage is enabled in your account
pinnacle.sports    # only after coverage probe
```

Run `sportsdata-mcp coverage` and inspect the live sport catalogue before making any of these primary.

## P0: use one odds adapter

```python
class DartsOddsProvider:
    async def fixtures_with_odds(self, start, end): ...
    async def event_markets(self, event_id): ...
```

Map provider output into the repo's existing snapshot schema rather than rewriting the app.

## P0: protect the 100-request/hour budget

```python
from dataclasses import dataclass

@dataclass
class RequestBudget:
    limit: int = 100
    reserve: int = 10
    used: int = 0

    def may_call(self, cost: int = 1) -> bool:
        return self.used + cost <= self.limit - self.reserve
```

Prefer schedule discovery once, then event-specific calls only for matches whose cached odds are stale.

## P1: steam movement based on immutable snapshots

```python
def implied_prob(decimal_odds):
    return 1 / decimal_odds


def probability_move(open_odds, current_odds):
    return implied_prob(current_odds) - implied_prob(open_odds)
```

Store:

```text
match_id
bookmaker
player_id
observed_at
decimal_odds
market_id
```

Then define “steam” using a reproducible threshold over a defined window, not visual intuition.

```python
is_steam = (
    abs(probability_move(open_odds, current_odds)) >= 0.04
    and minutes_elapsed <= 180
)
```

## P1: provider identity

Map Odds-API player/event ids to the existing canonical player identity map. Do not make sportsbook spelling the canonical identity.

## P2: coverage/status UI

```text
Fixtures: historical source OK
Odds API IO: 63/100 hourly calls remaining
DraftKings: 8 markets
BetMGM: 8 markets
Pinnacle: unavailable
Latest quote: 11m
```

## Tests

```python
def test_hourly_budget_keeps_reserve(): ...
def test_odds_provider_failure_not_no_fixtures(): ...
def test_steam_uses_two_timestamped_quotes(): ...
def test_player_alias_does_not_create_duplicate_player(): ...
```

## Bottom line

For darts, MCP is mostly **odds infrastructure**, not a new stats source. That is still useful: fewer direct provider quirks, better cache/budget control, immutable line movement and cleaner provenance.
