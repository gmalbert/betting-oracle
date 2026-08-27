# `nba-predictions` — SportsData MCP Review

## Fit

The repo already has `nba_api`, hoopR, Basketball Reference, The Odds API, ESPN/Rotowire and a mature pre-cache workflow. MCP should be a **redundancy and normalization layer**, not a replacement for hoopR or Basketball Reference research.

## Best groups

```text
nba.public.cdn
nba.stats
espn.*
theoddsapi.*
sportsgameodds.*
sportsdataio.*   # optional DFS/projection research
```

The reference NBA dispatcher covers the broad `stats.nba.com` surface, while the public CDN gives scoreboard/schedule/live box/play-by-play/odds.

## P0: adapter with failover

```python
class BasketballSource:
    async def scoreboard(self, date): ...
    async def boxscore(self, game_id): ...
    async def player_stats(self, player_id, season): ...


class CompositeBasketballSource(BasketballSource):
    def __init__(self, native, mcp):
        self.native = native
        self.mcp = mcp

    async def scoreboard(self, date):
        try:
            data = await self.native.scoreboard(date)
            if data:
                return {"source": "nba_api", "data": data}
        except Exception as exc:
            native_error = str(exc)
        data = await self.mcp.call("nba_scoreboard", game_date=date)
        return {"source": "sportsdata:nba.public.cdn", "data": data}
```

Discover/pin exact tool arguments in tests; do not couple downstream code to them.

## P1: lineup/injury readiness gate

Use ESPN plus existing sources to build a timestamped availability object:

```python
@dataclass
class TeamAvailability:
    team_id: str
    observed_at: datetime
    confirmed_starters: int
    questionable_minutes_share: float
    out_minutes_share: float
    source_count: int
```

Do not overwrite yesterday's injury state with today's status in historical training.

## P1: multi-book market layer

Collect moneyline/spread/total plus props into the common quote ledger.

```python
NBA_MARKETS = {
    "moneyline": ["home", "away"],
    "spread": ["home", "away"],
    "total": ["over", "under"],
}
```

Derived features:

```text
spread_median
spread_std
spread_open_to_current
total_median
total_std
home_no_vig_consensus
book_count
best_price_delta_vs_consensus
```

Keep market features out of any “pure basketball” benchmark model so you can measure how much signal is genuinely independent of the market.

## P1: Pick 6/player-prop identity

For props, use stable IDs:

```python
def canonical_prop(game_id, player_id, stat, period="game"):
    return f"nba:{game_id}:{player_id}:{stat}:{period}"
```

`sportsgameodds` is worth evaluating specifically because cross-book/time-stable market ids are useful for historical line tracking. `sportsdataio` can supply DFS salaries/projections if you want a separate market-expectation benchmark.

## P2: official endpoint snapshot tests

NBA endpoint shapes drift. Add golden fixtures from actual responses:

```python
@pytest.mark.contract
def test_scoreboard_contract(sample_scoreboard):
    assert sample_scoreboard["games"]
    game = sample_scoreboard["games"][0]
    assert "gameId" in game
    assert "homeTeam" in game
    assert "awayTeam" in game
```

Never make the model pipeline depend on undocumented columns without a contract test.

## P2: feature-source lineage

Add to `model_manifest.json`:

```json
{
  "feature_sources": {
    "rolling_net_rating": "hoopr",
    "injury_minutes_share": "espn",
    "market_spread_consensus": "sportsdata:multi_book",
    "team_box": "nba_api"
  }
}
```

## Bottom line

The highest-value change is to make the existing rich data stack more resilient and auditable: official NBA fallback, timestamped lineup/injury state, and stable multi-book/player-prop market snapshots.
