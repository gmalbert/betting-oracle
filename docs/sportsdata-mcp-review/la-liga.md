# `la-liga` — SportsData MCP Review

## Best opportunity

This repo still has several standalone acquisition paths: football-data.co.uk history, football-data.org fixtures, FBref xG, The Odds API and an ensemble trained at app level. The reference MCP adds a **dedicated LaLiga API backed by Opta data**, ESPN fallback, and historical closing odds via Football-Data.co.uk.

## Recommended groups

```text
laliga.core
laliga.teams
laliga.players
laliga.matches
footballdatauk.history
espn.*
theoddsapi.*
pinnacle.sports
```

## P0: migrate provider logic toward `pitch-oracle-core`

The long-term improvement is architectural: this repo should eventually become a thin consumer like EPL rather than maintaining a parallel soccer stack.

Until then, add one adapter:

```python
class LaLigaOfficialAdapter:
    async def teams(self, season): ...
    async def standings(self, season): ...
    async def players(self, season): ...
    async def fixtures(self, season): ...
    async def match(self, match_slug): ...
```

Downstream code should receive canonical frames, not MCP payloads.

## P1: enrich the sports-only model

Potential official pregame features:

```text
rolling team Opta metrics
squad continuity
player availability proxy
recent player/team form
match-event-derived disciplinary load
```

Keep bookmaker implied probabilities out of a **fundamental-only benchmark**. Train/evaluate:

```text
fundamental-only
market-only
hybrid
```

## P1: use Football-Data.co.uk closing odds for historical market baseline

Because the current model uses bookmaker probabilities, historical quote semantics matter. Store the exact source columns and distinguish closing from current/live lines.

```python
@dataclass
class HistoricalMarket:
    match_key: str
    bookmaker: str
    home_odds: float
    draw_odds: float
    away_odds: float
    market_timestamp_type: str  # e.g. closing/published
```

Do not label a season CSV closing line as a timestamped opening line.

## P1: source drift monitoring

The LaLiga API ships a public subscription key that may rotate. Treat 401 as a provider-health state, not an empty response.

```python
if status_code == 401:
    health = "AUTH_ROTATED_OR_INVALID"
```

## P2: UI

Add source badges to Markets/Stats:

```text
Official stats: LaLiga/Opta • refreshed 38m ago
Odds: 5 books • median age 12m
Historical market: Football-Data.co.uk closing
```

## Tests

```python
def test_laliga_auth_failure_not_empty_table(): ...
def test_historical_market_label_is_closing(): ...
def test_fundamental_model_excludes_market_features(): ...
def test_provider_ids_map_to_canonical_clubs(): ...
```

## Bottom line

The dedicated LaLiga/Opta feed is a meaningful enrichment. The larger win is consolidating this standalone league into the shared core architecture over time.
