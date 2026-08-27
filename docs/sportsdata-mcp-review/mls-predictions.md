# `mls-predictions` — SportsData MCP Review

## Strategy

Keep American Soccer Analysis as the distinctive xG/goals-added source. MCP should strengthen **fixtures, odds, source health and automation**.

## Recommended groups

```text
espn.*
footballdataorg.*
sportmonks.*
theoddsapi.*
oddsapiio.*
pinnacle.sports
```

Only enable providers after `sportsdata-mcp coverage` confirms the required MLS competition is actually exposed.

## P0: finish the planned nightly pipeline around a provider contract

```python
class MLSProviderBundle:
    async def fixtures(self, start, end): ...
    async def standings(self): ...
    async def odds(self, event_id): ...
    async def provider_health(self): ...
```

Write provider outputs into cache/artifacts before Streamlit loads them.

## P1: preserve MLS-specific features

MCP is not a reason to flatten MLS into a generic European model. Keep:

```text
travel distance
artificial turf
conference structure
playoff race
Designated Player availability
ASA xG/goals-added
```

Add market-state features only after collecting them prospectively:

```text
1x2_consensus
book_dispersion
open_to_current_move
best_price
quote_age
```

## P1: availability snapshot

```python
@dataclass
class RosterSnapshot:
    team_id: str
    observed_at: datetime
    dp_available_count: int | None
    key_players_out: tuple[str, ...]
    source: str
```

Do not infer historical DP availability from current rosters.

## P2: provider confidence in the UI

```text
ASA xG             fresh 8h
Fixtures           ESPN + secondary agree
Odds               4 books / 19m old
Roster context     partial
```

## Tests

```python
def test_asa_features_remain_primary(): ...
def test_cross_country_travel_feature_survives_provider_refactor(): ...
def test_market_feature_asof_cutoff(): ...
def test_provider_failure_does_not_create_fake_offseason(): ...
```

## Bottom line

Use MCP to make the planned production pipeline more reliable while preserving the MLS-specific feature engineering that differentiates this project.
