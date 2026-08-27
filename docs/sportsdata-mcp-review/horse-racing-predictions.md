# `horse-racing-predictions` — SportsData MCP Review

## The core opportunity

The repo already states the key limitation correctly: the walk-forward backtester cannot validate value betting until **real historical bookmaker odds** are joined. `sportsdata-mcp` has unusually deep racing coverage—fixed odds, tote pools, exchange prices, movers, form, results, and racecards across multiple providers.

The first goal should therefore be **market capture and identity resolution**, not another horse-performance model.

## Provider strategy

Because several reference providers are Australian and geo-restricted, treat provider availability as deployment-specific.

```text
UK model/history       current repo remains primary
Exchange benchmark     Betfair when reachable/appropriate
US racing fallback     FanDuel racing where relevant
AU racecards/markets   Sportsbet/TAB/PointsBet/BetR/Entain only when reachable
Supplementary          Racing & Sports
```

Never treat a geo-block as “no races today.”

## P0: canonical race and runner ids

Create two registries:

```text
data/processed/identity/races.parquet
data/processed/identity/runners.parquet
```

Race identity:

```text
race_key
race_date
course_key
scheduled_time_utc
distance_m
discipline
provider
provider_race_id
confidence
```

Runner identity:

```text
runner_key
horse_name
foaling_year
provider
provider_runner_id
provider_race_id
cloth_number
barrier
```

A robust race key:

```python
from hashlib import sha1


def make_race_key(date, course, scheduled_time, distance_m):
    raw = f"{date}|{course.casefold().strip()}|{scheduled_time}|{round(distance_m / 10) * 10}"
    return sha1(raw.encode()).hexdigest()[:16]
```

Use fuzzy matching only to propose mappings. Persist reviewed mappings so identities do not change from run to run.

## P0: immutable odds ladder

```python
from pydantic import BaseModel
from datetime import datetime


class RacingQuote(BaseModel):
    race_key: str
    runner_key: str
    provider: str
    market_type: str  # fixed_win, fixed_place, exchange_back, exchange_lay, tote_win
    decimal_odds: float
    available_size: float | None = None
    observed_at: datetime
    provider_market_id: str | None = None
    provider_runner_id: str | None = None
```

Write snapshots append-only:

```text
data/markets/racing_quotes/YYYY/MM/DD/quotes.parquet
```

Do not update yesterday's file with today's interpretation. Data corrections should be separate versioned reconciliation artifacts.

## P0: add true value-bet backtesting

Once historical/collected market prices exist:

```python
def flat_stake_profit(won: bool, odds: float, stake: float = 1.0) -> float:
    return stake * (odds - 1.0) if won else -stake


def expected_value(p_win: float, odds: float) -> float:
    return p_win * odds - 1.0
```

Selection contract:

```python
MIN_EDGE = 0.03
MIN_EV = 0.02
MAX_QUOTE_AGE_MIN = 30

is_candidate = (
    (model_prob - market_fair_prob >= MIN_EDGE)
    & (model_prob * offered_odds - 1 >= MIN_EV)
    & (quote_age_minutes <= MAX_QUOTE_AGE_MIN)
)
```

The backtest should explicitly report:

```text
number of candidate races
number of bets
win rate
average offered odds
average closing odds
ROI
CLV
max drawdown
Brier score
calibration by probability bucket
results by field size/class/course/price band
```

## P1: exchange-derived market intelligence

Exchange back/lay information can add market-quality features that fixed odds alone cannot.

Potential features:

```text
best_back
best_lay
exchange_midpoint
exchange_spread_pct
exchange_available_back
exchange_available_lay
fixed_vs_exchange_delta
minutes_to_post
price_move_30m
price_move_10m
```

```python
def exchange_mid(back: float | None, lay: float | None) -> float | None:
    if back is None or lay is None or back <= 1 or lay <= 1:
        return None
    # Convert prices to probability, average, convert back.
    p = ((1 / back) + (1 / lay)) / 2
    return 1 / p
```

Use the exchange price primarily as a market benchmark; do not assume all exchange liquidity is executable at displayed prices.

## P1: racecard/form enrichment

Where provider racecards add data absent from the current historical set, normalize only pre-race fields such as:

```text
runner_status
barrier/draw
weight
jockey
trainer
gear changes
fixed opening price
current fixed price
place terms
scratch status
```

Never ingest provider-calculated post-race ratings into a pre-race training row unless their publication timestamp proves they were available beforehand.

## P1: race-level market shape

Your current race profitability scorer can be enriched with **market competitiveness**:

```python
import numpy as np


def normalized_entropy(probs):
    p = np.asarray([x for x in probs if x > 0], dtype=float)
    p /= p.sum()
    if len(p) <= 1:
        return 0.0
    return float(-(p * np.log(p)).sum() / np.log(len(p)))
```

Features:

```text
market_entropy
favorite_fair_prob
second_favorite_fair_prob
favorite_gap
num_runners_below_10_0
num_runners_below_20_0
book_overround
exchange_spread_median
```

These may help distinguish genuinely competitive races from superficially large fields.

## P1: steam/drift research

For every runner:

```python
def pct_price_move(open_odds: float, current_odds: float) -> float:
    return (current_odds - open_odds) / open_odds
```

Store both odds movement and probability movement. Price changes are nonlinear in probability space.

```python
def prob_move(open_odds: float, current_odds: float) -> float:
    return (1 / current_odds) - (1 / open_odds)
```

Research questions:

- Do your top model picks shorten more than controls?
- Does early positive CLV predict long-run ROI?
- Are drifters systematically overestimated by the model?
- Is the signal stronger in the repo's Tier 1 races?

## P2: tote/fixed/exchange disagreement

For providers exposing multiple market mechanisms, build disagreement features:

```text
fixed_implied_prob
exchange_implied_prob
tote_implied_prob
fixed_exchange_delta
tote_exchange_delta
```

Do not compare tote prices before settlement as though they were guaranteed final payouts; label them according to the provider semantics.

## P2: live scratch handling

A scratch should invalidate old field-relative features.

```python
@dataclass(frozen=True)
class FieldSnapshot:
    race_key: str
    observed_at: datetime
    active_runner_keys: tuple[str, ...]

    @property
    def field_size(self) -> int:
        return len(self.active_runner_keys)
```

When the active field changes, recompute:

- normalized model probabilities;
- market overround/no-vig probabilities;
- exacta/trifecta estimates;
- field-relative age/rating features.

## GitHub Actions

```yaml
name: Racing market snapshots
on:
  workflow_dispatch:
  schedule:
    - cron: "13 * * * *"

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
      - run: sportsdata-mcp coverage
        env:
          SPORTSDATA_MCP_GROUPS: "betfair.*,fanduel.racing,racingandsports.racing"
      - run: python scripts/snapshot_sportsdata_racing.py
```

Only enable providers that succeed from the actual runner location.

## Tests

```python
def test_geo_block_is_provider_status_not_empty_racecard(): ...
def test_scratched_runner_removed_from_current_field(): ...
def test_historical_backtest_uses_quote_before_cutoff(): ...
def test_market_overround_computed_per_race_snapshot(): ...
def test_runner_identity_stable_across_providers(): ...
def test_exchange_back_not_confused_with_lay(): ...
def test_clv_uses_comparable_market_type(): ...
```

## Expected payoff

The market layer is the missing bridge between a calibrated horse probability and a defensible betting strategy. If only one change is made from this review, make it **timestamped runner-level market capture with stable identities**. Everything else—CLV, steam/drift, exchange benchmarks, honest ROI, and richer race scoring—follows from that foundation.
