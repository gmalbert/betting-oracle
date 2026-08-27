# `nfl-predictions` — SportsData MCP Review

## Strategy

Keep NFLverse as the authoritative play-by-play/history source. Use `sportsdata-mcp` for **ESPN/source fallback, market snapshots, and player-prop market identity**.

## Recommended groups

```text
espn.*
theoddsapi.*
oddsapiio.*
sportsgameodds.*
sportsdataio.*   # optional DFS salaries/projections
```

## P0: make historical performance market-aware

The repo's very high selective-bet win-rate claims should always be accompanied by quote timing, sample count and out-of-sample period. Create one settled recommendation record:

```python
@dataclass
class SettledRecommendation:
    game_id: str
    generated_at: datetime
    market: str
    side: str
    line: float | None
    price_decimal: float
    model_probability: float
    market_fair_probability: float
    result: str
    profit_units: float
    closing_price_decimal: float | None
```

Then publish Wilson intervals and sample counts next to hit rates.

```python
from statsmodels.stats.proportion import proportion_confint

lo, hi = proportion_confint(wins, bets, alpha=.05, method="wilson")
```

## P0: immutable spread/total/ML snapshots

Use the shared `MarketQuote` ledger. For spread movement, keep both **line and price**—`+3 -110` and `+2.5 +100` are different states.

```text
market_key
event_key
book
side
line
price
observed_at
```

## P1: Pick 6 / player props

`sportsgameodds` is particularly relevant because stable market ids improve joining the same prop across books and timestamps.

```python
@dataclass(frozen=True)
class PropContract:
    game_id: str
    player_id: str
    stat: str
    period: str
    line: float
```

Collect lines prospectively and evaluate calibration conditional on the line—not only raw prediction MAE.

```python
def over_probability(mu, sigma, line):
    from scipy.stats import norm
    return float(1 - norm.cdf(line, loc=mu, scale=sigma))
```

## P1: availability/news state

Use ESPN only as supplemental current-state data. Timestamp QB/injury/depth-chart observations and hash them into prediction dependencies.

```python
prediction_context_hash = hash((
    game_id,
    feature_snapshot_id,
    injury_snapshot_id,
    market_snapshot_id,
    model_version,
))
```

## P2: market-vs-model benchmarks

Maintain three explicit models:

```text
sports_only_model
market_only_baseline
sports_plus_market_model
```

Compare Brier/log loss/ATS/ROI out of sample. This prevents a model from appearing predictive merely because it re-learns the sportsbook line.

## Tests

```python
def test_player_prop_line_is_observed_before_prediction(): ...
def test_spread_line_and_price_move_together(): ...
def test_nflverse_remains_primary_history_source(): ...
def test_reported_hit_rate_includes_n_and_interval(): ...
```

## Bottom line

Do not replace NFLverse. Use MCP to turn the betting side into a timestamped multi-book experiment and make player-prop market tracking much more defensible.
