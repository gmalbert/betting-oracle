# `golf-predictions` — SportsData MCP Review

## Best opportunity: make DataGolf a first-class enrichment source

This repo currently combines PGA/ESPN scraping, OWGR, weather, and The Odds API. The `sportsdata-mcp` DataGolf integration is unusually well aligned with the roadmap: field data, rankings, pre-tournament probabilities, in-play probabilities, skill decomposition, live strokes-gained, DFS projections, bookmaker odds, and historical bookmaker odds.

Do **not** throw away the existing scraper/history. Use DataGolf as a high-quality parallel source and benchmarking layer.

## Recommended provider stack

```text
Primary historical results: current repo datasets/scrapers
Identity/bootstrap:       ESPN + existing player registry
Premium enrichment:       datagolf.*
Market redundancy:        theoddsapi.* / pinnacle.sports where available
Weather:                  existing Open-Meteo path
```

## P0: canonical golfer identity table

Golf joins fail because names change formatting and tours use different ids. Extend the current stable player-id work into a provider map.

```text
data_files/player_provider_ids.parquet

canonical_player_id
canonical_name
espn_id
datagolf_id
owgr_id
pga_id
aliases
last_verified_at
```

```python
from __future__ import annotations

import re
import unicodedata


def normalize_name(name: str) -> str:
    text = unicodedata.normalize("NFKD", name)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.casefold().strip()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return " ".join(text.split())
```

Never use the normalized string as the permanent id; use it only to establish a reviewed mapping.

## P0: DataGolf enrichment cache

Keep external data out of Streamlit runtime.

```python
# scripts/fetch_datagolf_enrichment.py
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from sports_gateway import open_sportsdata

OUT = Path("data_files/provider_cache/datagolf")


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    async with open_sportsdata("datagolf.*") as sd:
        payloads = {
            "field": await sd.call("datagolf_field"),
            "rankings": await sd.call("datagolf_rankings"),
            "pre_tournament": await sd.call("datagolf_pre_tournament_predictions"),
        }

    stamp = datetime.now(timezone.utc).isoformat()
    for name, payload in payloads.items():
        (OUT / f"{name}.json").write_text(
            json.dumps(
                {"fetched_at": stamp, "payload": payload},
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    asyncio.run(main())
```

Tool names should be confirmed with `list-tools`/capability discovery in the installed version; keep them in config rather than scattering strings through model code.

## P1: use external model probabilities as benchmark features, not labels

DataGolf's pre-tournament model can be valuable in three ways:

1. benchmark your model;
2. ensemble only after out-of-sample evidence supports it;
3. create disagreement features.

Example feature frame:

```python
features["dg_win_prob"] = ...
features["our_minus_dg_prob"] = features["model_win_prob"] - features["dg_win_prob"]
features["market_minus_dg_prob"] = features["market_implied"] - features["dg_win_prob"]
```

Do not train a model to reproduce DataGolf and then call the agreement independent evidence.

### Benchmark report

```python
from sklearn.metrics import brier_score_loss, log_loss


def benchmark_probs(df):
    settled = df.dropna(subset=["won", "model_win_prob", "dg_win_prob"])
    return {
        "ours_brier": brier_score_loss(settled.won, settled.model_win_prob),
        "dg_brier": brier_score_loss(settled.won, settled.dg_win_prob),
        "ours_logloss": log_loss(settled.won, settled.model_win_prob),
        "dg_logloss": log_loss(settled.won, settled.dg_win_prob),
    }
```

For a tournament winner market, calibration/top-N and ranking metrics may be more informative than binary accuracy alone.

## P1: strokes-gained decomposition

The current repo already values SG features. Add provider-derived snapshots such as:

```text
sg_ott
sg_app
sg_arg
sg_putt
sg_total
approach_skill_long
approach_skill_mid
approach_skill_short
course_fit_component
field_strength
```

All rolling/player-form features must use only events completed before the prediction timestamp.

## P1: historical market odds for honest backtesting

This is one of DataGolf's strongest advantages over scraping only today's prices.

Create:

```text
data_files/markets/golf_market_snapshots.parquet
```

Columns:

```text
event_id
player_id
market_type
bookmaker
observed_at
is_closing
decimal_odds
implied_prob
source
```

Then backtest on the actual quote available at your simulated prediction time.

```python
def expected_value(prob: float, decimal_odds: float) -> float:
    return prob * decimal_odds - 1.0
```

For each historical selection:

```python
edge = model_prob - market_no_vig_prob
ev = expected_value(model_prob, offered_decimal)
```

Require both positive probability edge **and** positive EV after vig.

## P1: matchup market model

Outright winner markets are noisy and high variance. DataGolf's matchup data creates a cleaner supervised target.

Add a paired-difference feature builder:

```python
PAIR_FEATURES = [
    "sg_total_rolling",
    "sg_app_rolling",
    "sg_putt_rolling",
    "course_history_sg",
    "recent_finish_strength",
    "field_strength_adjusted_form",
]


def make_pair_features(a, b):
    return {
        f"delta_{c}": float(a[c]) - float(b[c])
        for c in PAIR_FEATURES
    }
```

Train with tournament-grouped time splits so golfers from the same event never leak across train/test.

## P2: live/in-play research mode

DataGolf exposes in-play probabilities and live SG. Keep this separate from the pre-tournament model.

Suggested architecture:

```text
pre_tournament_model.pkl
in_play_model.pkl
live_snapshots.parquet
```

Never overwrite the pre-event prediction with a later in-play forecast; preserve both for evaluation.

Live feature candidates:

```text
holes_remaining
current_position
strokes_to_lead
live_sg_total
live_sg_app
live_sg_putt
weather_next_3h
course_wave_advantage
market_move_since_tee_time
```

## P2: course data enrichment

The keyed `golfcourseapi` provider can supplement per-hole par/yardage/stroke index for course embeddings.

Potential embedding inputs:

```text
par_3_count
par_4_count
par_5_count
avg_par3_yards
avg_par4_yards
avg_par5_yards
front9_yards
back9_yards
long_hole_share
short_par4_share
```

This is a better basis for course similarity than course name alone.

## CI provider gate

```yaml
- name: DataGolf provider smoke
  env:
    DATAGOLF_KEY: ${{ secrets.DATAGOLF_KEY }}
    SPORTSDATA_MCP_GROUPS: "datagolf.general,datagolf.predictions,datagolf.betting"
  run: sportsdata-mcp coverage
```

Do not run expensive historical downloads every CI invocation; cache raw provider responses and refresh them intentionally.

## UI additions

Add a **Market & Benchmark** expander to each tournament/player card:

```text
Our win probability       4.8%
DataGolf benchmark        4.3%
Market no-vig consensus   3.6%
Best available price      +2800
Expected value            +39.2%
Books observed            8
Quote age                 17 min
```

Also show a `Source health` badge so a missing DataGolf response does not masquerade as a zero probability.

## Expected payoff

This integration can materially improve this repo because it supplies exactly the data categories golf modeling is otherwise expensive to scrape well: field strength, SG decomposition, historical market prices, matchup pricing, and live tournament state. The highest priority is **benchmarking and historical odds**, not immediately adding more model complexity.
