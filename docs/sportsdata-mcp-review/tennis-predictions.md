# `tennis-predictions` — SportsData MCP Review

## Highest-value changes

The current stack has strong historical inputs but a fragile/live-data bottleneck: Matchstat RapidAPI is budgeted at 500 calls/month, and player identity matching is already a major concern. `sportsdata-mcp` gives this repo two especially useful paths:

- **WTA official data** (`wta.tennis`) for rankings, players, histories, tournament calendars/results/entries.
- **API-Tennis** (`apitennis.*`, keyed) for ATP/ITF coverage, H2H, rankings and draws.
- Generic odds providers for market snapshots and redundancy.

Keep TennisMyLife and tennis-data.co.uk as historical foundations.

## Provider hierarchy

```python
TENNIS_SOURCE_POLICY = {
    "wta": ["wta", "espn", "existing"],
    "atp": ["apitennis", "existing"],
    "itf": ["apitennis", "existing"],
    "odds": ["theoddsapi", "oddsapiio", "existing_matchstat"],
}
```

## P0: provider-aware player registry

Extend name normalization into stable ids:

```text
canonical_player_id
canonical_name
tour
wta_id
apitennis_id
matchstat_id
sportsbook_aliases
country
dob
handedness
verified_at
```

Use DOB/country/tour as disambiguators; never merge two players solely because normalized names match.

```python
def candidate_score(a, b):
    score = 0
    if a.normalized_name == b.normalized_name:
        score += 70
    if a.dob and b.dob and a.dob == b.dob:
        score += 20
    if a.country and b.country and a.country == b.country:
        score += 10
    return score
```

Require manual review below a high-confidence threshold.

## P0: reduce live API spend through schedule-first fetching

Instead of querying a paid endpoint for every possible player/match:

```text
1. Fetch today's tournament/event list.
2. Resolve only scheduled players.
3. Check local cache freshness.
4. Request only missing/stale player data.
5. Fetch odds only for matched event ids.
```

```python
async def missing_player_ids(registry, scheduled_ids, max_age_hours=24):
    now = pd.Timestamp.utcnow()
    rows = registry[registry.canonical_player_id.isin(scheduled_ids)]
    stale = rows[
        rows.last_refreshed.isna()
        | ((now - pd.to_datetime(rows.last_refreshed, utc=True)) > pd.Timedelta(hours=max_age_hours))
    ]
    return stale.canonical_player_id.tolist()
```

## P1: official WTA features

Point-in-time candidate features:

```text
ranking
ranking_delta_7d
ranking_delta_30d
seed
entry_status
recent_match_count
recent_win_pct
surface_recent_win_pct
retirement_count_90d
```

Do not use a ranking published after the match date in historical training.

## P1: ATP/ITF coverage gap

The current UI leaves cells blank for players without ATP main-tour history. API-Tennis can make those states explicit:

```text
coverage_tier = MAIN_TOUR | CHALLENGER | ITF | UNKNOWN
```

Then train or calibrate separately by coverage tier instead of silently mixing sample quality.

```python
def prediction_readiness(row):
    if row.coverage_tier == "UNKNOWN":
        return "ABSTAIN_NO_HISTORY"
    if row.prior_matches < 8:
        return "LOW_SAMPLE"
    return "READY"
```

## P1: market snapshots / line movement

Canonical tennis quote:

```text
event_key
player_id
bookmaker
market=moneyline
selection
observed_at
decimal_odds
no_vig_prob
```

For two-way markets:

```python
def devig(p_a, p_b):
    z = p_a + p_b
    return p_a / z, p_b / z
```

Features:

```text
open_no_vig_prob
current_no_vig_prob
market_move
book_dispersion
best_price
consensus_price
quote_age
```

## P2: tournament-context features

Official entry lists/calendars enable:

- qualifying vs direct entry;
- seed status;
- days since previous match;
- matches played in previous 7/14 days;
- travel/tournament transition;
- best-of-3 vs best-of-5 contract;
- tournament tier.

Keep surface as a core interaction term.

## P2: source-consistency test

When WTA and historical source overlap, monitor disagreement:

```python
def compare_result_sources(a, b):
    return {
        "winner_match": a.winner_id == b.winner_id,
        "score_match": a.score == b.score,
        "date_delta_hours": abs((a.start_time - b.start_time).total_seconds()) / 3600,
    }
```

A discrepancy report is more valuable than silently picking one source.

## CI

```yaml
- name: Tennis provider coverage
  env:
    API_TENNIS_KEY: ${{ secrets.API_TENNIS_KEY }}
    SPORTSDATA_MCP_GROUPS: "wta.tennis,apitennis.*,theoddsapi.*"
  run: sportsdata-mcp coverage
```

## Bottom line

Use MCP first to reduce live-source fragility, improve WTA/ATP/ITF identity and coverage, and collect timestamped odds. Do not replace the historical feature pipeline merely because another endpoint exists.
