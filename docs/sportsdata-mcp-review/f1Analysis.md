# `f1Analysis` — SportsData MCP Review

## Strategy

Keep **F1DB + FastF1** as primary historical/analysis sources. Your `f1bet` package already has the right contracts: point-in-time features, grouped walk-forward validation, timestamped odds/forecast ledgers and an odds-required backtester.

The useful MCP additions are **OpenF1**, **Jolpica F1**, and market/provider redundancy.

## Source roles

```text
F1DB        canonical broad history / entity data
FastF1      deep session timing/telemetry and current pipeline
OpenF1      independent live timing, telemetry, weather, race control
Jolpica     long-history schedule/results/standings fallback
Odds        multi-provider timestamped market observations
```

## P0: independent validation feed

Use OpenF1 to validate key derived session facts rather than merging blindly.

```python
@dataclass(frozen=True)
class SessionCrossCheck:
    meeting_key: str
    session_key: str
    metric: str
    fastf1_value: float | str | None
    openf1_value: float | str | None
    agrees: bool
    tolerance: float | None = None
```

Good cross-check targets:

```text
session start/end
classification
starting grid
lap count
pit stops
safety-car/race-control periods
weather
sector/lap timing
```

## P1: new point-in-time features

OpenF1 can make some live/session state easier to collect consistently:

```text
long_run_pace_delta
sector_consistency
speed_trap_rank
pit_stop_loss
stint_degradation
track_temp
rainfall
wind_speed
race_control_incident_count
recent_gap_to_teammate
```

Every feature must carry `session_key`, `observed_at`, and a cutoff contract.

```python
def allowed_before_race(feature_time, race_start):
    return feature_time < race_start
```

For a pre-practice model, practice/quali features are forbidden even though they exist in the database later.

## P1: odds ledger by prediction phase

Define separate forecast contracts:

```text
PRE_WEEKEND
POST_FP1
POST_FP2
POST_FP3
POST_QUALIFYING
PRE_RACE
```

```python
@dataclass(frozen=True)
class ForecastSnapshot:
    race_id: str
    phase: str
    generated_at: datetime
    feature_cutoff: datetime
    market_cutoff: datetime
    model_version: str
```

CLV must compare a phase quote with a later closing quote, never with a quote already known when reconstructing the old forecast.

## P2: Jolpica as historical integrity check

Use Jolpica for coverage assertions:

```python
assert set(f1db_races["year_round"]) >= set(model_rows["year_round"])
```

Generate a discrepancy report for winner/grid/result mismatches instead of silently overwriting F1DB.

## P2: provider-health panel

Expose in the Betting Research tab:

```text
F1DB       local     OK
FastF1     820 ms    OK
OpenF1     245 ms    OK
Jolpica    301 ms    OK
Odds       3 books   DEGRADED
```

## Tests

```python
def test_pre_weekend_contract_rejects_practice_features(): ...
def test_openf1_session_maps_one_to_one_to_race(): ...
def test_market_quote_precedes_forecast_cutoff(): ...
def test_crosscheck_disagreement_does_not_overwrite_primary(): ...
```

## Bottom line

MCP improves **independent validation and live/session redundancy**. It should not replace the sophisticated F1DB/FastF1 pipeline already built here.
