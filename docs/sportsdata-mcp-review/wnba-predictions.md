# `wnba-predictions` — SportsData MCP Review

## Strategy

Keep wehoop historical data and the WNBA-specific leakage-safe modeling rules. Use MCP mainly for **ESPN redundancy and market collection**. Do not assume every NBA-specific tool supports WNBA until a live contract test proves it.

## P0

Enable only verified groups:

```text
espn.*
theoddsapi.*
oddsapiio.*
```

Probe any NBA Stats/WNBA league-id path in shadow mode before adding it to production.

```python
@dataclass(frozen=True)
class SourceCapability:
    name: str
    verified_for_wnba: bool
    last_probe: datetime
    notes: str = ""
```

Persist this rather than relying on a README assumption.

## Market snapshots

Reuse the NBA canonical quote model, but keep league explicit:

```python
quote = MarketQuote(
    sport="basketball",
    league="wnba",
    event_key=game_id,
    bookmaker=book,
    market="spread",
    selection=team_id,
    line=line,
    decimal_odds=odds,
    observed_at=now,
    provider=provider,
)
```

Useful features:

```text
spread_consensus
spread_dispersion
total_consensus
moneyline_no_vig_consensus
book_count
quote_age
market_move_24h
```

## Availability data

ESPN can remain a useful current-season source for schedule/rosters/injuries/officials. Timestamp all injury observations:

```text
player_id
team_id
status
reported_at
observed_at
source
```

Historical training must use the last status observed before the model cutoff.

## Data-health states

WNBA samples can be smaller, so distinguish data availability from model confidence:

```text
READY
LOW_SAMPLE
SOURCE_STALE
MARKET_MISSING
MARKET_STALE
INJURY_STATE_UNCERTAIN
```

## Tests

```python
def test_no_nba_assumption_in_wnba_team_count(): ...
def test_provider_is_verified_before_use(): ...
def test_injury_status_is_asof_cutoff(): ...
def test_market_quotes_are_league_scoped(): ...
```

## Bottom line

This should be a conservative integration: improve source resilience and market history without importing NBA-specific assumptions into the WNBA port.
