# `cricket` — SportsData MCP Review

## Fit

Wicket Oracle already has production-grade pipeline semantics: no mock production data, atomic cache promotion, manifests, explicit competition states, validation gates, settlement and CLV. Preserve all of that. MCP should simply become another **provider adapter family**.

## Strong additions

```text
cricketaustralia.*  # free official AU fixture/scorecard/ladder data
cricketdata.*       # existing provider through common gateway
entitysport.*       # ball-by-ball commentary/deeper feed
espn.*              # fallback where covered
theoddsapi.*
oddsapiio.*
pinnacle.sports
```

Keep Cricsheet as the historical ball-by-ball foundation.

## P0: provider hierarchy by competition

```python
SOURCE_POLICY = {
    "bbl": {
        "fixtures": ["cricketaustralia", "cricketdata"],
        "scorecard": ["cricketaustralia", "cricketdata"],
        "history": ["cricsheet"],
    },
    "international": {
        "fixtures": ["cricketdata", "espn"],
        "history": ["cricsheet"],
    },
}
```

## P0: map MCP errors into existing production states

```python
MCP_TO_APP_STATE = {
    "AUTH_REQUIRED": "fetch_failed",
    "QUOTA_EXHAUSTED": "fetch_failed",
    "GEO_BLOCKED": "fetch_failed",
    "EMPTY_OK": "no_fixtures",
}
```

Critically, only `EMPTY_OK` after a successful provider call may become `no_fixtures`.

## P1: ball-by-ball source benchmarking

For overlapping matches, compare Cricsheet with EntitySport before using it as enrichment:

```text
innings count
runs
wickets
overs/balls
batter ids
bowler ids
dismissal types
```

```python
def innings_checksum(df):
    return (
        int(df.total_runs.sum()),
        int(df.is_wicket.sum()),
        int(len(df)),
    )
```

Write mismatches to a QA artifact; never overwrite Cricsheet silently.

## P1: Cricket Australia enrichment

For Australian competitions, official scorecards can support:

- current squad/player identity;
- fixture changes;
- innings scorecard validation;
- venue ids;
- current competition ladder;
- live state.

## P1: expand market state

The current DK comparison can become:

```text
book_count
best_match_winner_price
no_vig_match_consensus
consensus_dispersion
opening/current move
total-line dispersion
prop best price
quote age
```

All existing CLV logic can then use a better closing benchmark.

## P2: prediction publication gate

Add provider health to the existing six gates:

```python
publish = all([
    model_valid,
    historical_data_valid,
    fixture_identity_valid,
    source_manifest_valid,
    market_state_valid_or_not_required,
    cache_atomicity_valid,
])
```

## Tests

```python
def test_provider_quota_error_never_maps_to_no_fixtures(): ...
def test_cricketaustralia_match_identity_maps_to_cricsheet(): ...
def test_ball_by_ball_checksum_discrepancy_is_logged(): ...
def test_market_snapshot_participates_in_manifest_hash(): ...
```

## Bottom line

This repo already has the right production architecture. Integrate MCP inside it rather than redesigning it: Cricket Australia is the most interesting new free source, with EntitySport as a potential deeper keyed supplement.
