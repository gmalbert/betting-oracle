# `pitch-oracle-core` — SportsData MCP Review

## This is where the soccer integration belongs

The thin consumer architecture is exactly right. Do **not** independently wire `sportsdata-mcp` into every country/league repo. Add one provider-neutral implementation to `pitch-oracle-core`, release it, and let consumers opt into source groups through configuration.

## P0: extend `LeagueConfig` with source capabilities

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class SportsDataConfig:
    enabled: bool = False
    groups: tuple[str, ...] = ()
    fixture_sources: tuple[str, ...] = ()
    stats_sources: tuple[str, ...] = ()
    odds_sources: tuple[str, ...] = ()
    min_market_books: int = 2
    max_quote_age_minutes: int = 90


@dataclass(frozen=True)
class LeagueConfig:
    # existing fields...
    sportsdata: SportsDataConfig = field(default_factory=SportsDataConfig)
```

Example EPL consumer:

```python
sportsdata=SportsDataConfig(
    enabled=True,
    groups=(
        "premierleague.core",
        "premierleague.teams",
        "premierleague.matches",
        "premierleague.players",
        "premierleague.stats",
        "espn.*",
        "footballdatauk.history",
        "pinnacle.sports",
    ),
    fixture_sources=("premierleague", "espn"),
    stats_sources=("premierleague",),
    odds_sources=("pinnacle", "existing"),
)
```

## P0: provider protocol

```python
from typing import Protocol

class FootballProvider(Protocol):
    async def fixtures(self, *, start, end): ...
    async def standings(self, *, season): ...
    async def teams(self, *, season): ...
    async def match_stats(self, *, match_id): ...
    async def odds(self, *, match_id): ...
```

Implement `SportsDataFootballProvider` behind this protocol. Core pages/models should never call MCP tool names directly.

## P0: source registry by league

```python
SPORTSDATA_SOURCE_MAP = {
    "epl": {
        "official": "premierleague",
        "history_odds": "footballdatauk",
        "fallback": "espn",
    },
    "laliga": {
        "official": "laliga",
        "history_odds": "footballdatauk",
        "fallback": "espn",
    },
    "bundesliga": {
        "official": "openligadb",
        "history_odds": "footballdatauk",
        "fallback": "espn",
    },
}
```

For leagues with no dedicated reference provider, use ESPN/football-data.org/API providers only after coverage tests.

## P0: canonical match identity

```python
@dataclass(frozen=True)
class MatchIdentity:
    match_key: str
    league_key: str
    season: str
    kickoff_utc: datetime
    home_team_key: str
    away_team_key: str
    provider_ids: dict[str, str]
```

Provider-specific IDs belong in the identity registry, not model feature rows.

## P1: market observation contract

Add to core so every consumer gets identical CLV/movement behavior:

```python
@dataclass(frozen=True)
class FootballMarketQuote:
    match_key: str
    bookmaker: str
    market: str       # 1x2, total, btts, handicap
    selection: str
    line: float | None
    decimal_odds: float
    observed_at: datetime
    provider: str
```

Canonical market helpers:

```python
def devig_1x2(home, draw, away):
    raw = [1/home, 1/draw, 1/away]
    z = sum(raw)
    return tuple(p/z for p in raw)
```

Derived artifacts:

```text
precomputed/market_consensus.parquet
precomputed/market_movement.parquet
precomputed/provider_health.json
```

## P1: separate sports model from market model

Core should train/evaluate:

```text
fundamental_model      team/form/xG/etc only
market_baseline        no-vig consensus
hybrid_model           fundamental + market state
```

Report all three. A hybrid beating the fundamental model but not the market baseline is not a betting edge.

## P1: official source enrichment

Where official feeds expose Opta-level stats, add them through additive feature stores rather than rewriting historical datasets:

```text
data_files/model_features/provider_official_features.parquet
```

Columns should include:

```text
match_key
feature_asof
source_provider
team_key
shots
shots_on_target
possession
xg_if_available
corners
cards
... provider-specific raw fields
```

Convert to league-neutral model features in a second step.

## P1: artifact manifest extension

```json
{
  "core_version": "1.4.x",
  "league": "epl",
  "source_contract_version": 2,
  "sportsdata_mcp_version": "0.31.1",
  "provider_groups": ["premierleague.matches", "espn.scores"],
  "provider_health_sha256": "...",
  "market_snapshot_max_observed_at": "..."
}
```

Runtime should reject artifacts built against an incompatible source-contract version.

## P2: capability-based discovery

Do not make a league config depend solely on provider names. Allow capabilities:

```python
REQUIRED_CAPABILITIES = {
    "fixtures": "sport.fixtures_by_date",
    "standings": "stats.ladder",
    "event_markets": "sport.event_markets",
}
```

At smoke-test time, verify at least one enabled tool satisfies each required capability.

## P2: provider differential tests

```python
@pytest.mark.integration
async def test_fixture_sources_agree_on_next_round(...): ...

@pytest.mark.integration
async def test_official_and_espn_team_counts_are_plausible(...): ...

@pytest.mark.integration
async def test_market_quotes_are_before_kickoff(...): ...
```

## P2: reusable workflow

Add provider coverage before generating artifacts:

```yaml
- name: Sports provider doctor
  run: sportsdata-mcp coverage
  env:
    SPORTSDATA_MCP_GROUPS: ${{ inputs.sportsdata_groups }}
```

Then run the existing strict cache validation.

## Migration sequence

1. Add the interfaces and disabled config; release core.
2. Pilot EPL official feed + market ledger.
3. Add La Liga.
4. Add Bundesliga via OpenLigaDB.
5. Add one thin consumer without a dedicated official provider to validate fallback behavior.
6. Roll out to remaining consumers.

## Bottom line

This repo can turn `sportsdata-mcp` from 20 separate integration ideas into **one versioned provider contract shared by the entire soccer portfolio**. That is the architectural win.
