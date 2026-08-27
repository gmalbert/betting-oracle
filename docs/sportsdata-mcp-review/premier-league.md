# `premier-league` — SportsData MCP Review

## Recommendation: keep this repo thin

This consumer already delegates shared data preparation, training, validation, provider adapters and UI to `pitch-oracle-core`. Preserve that architecture. **Do not add an MCP client here.** Implement the integration in core and make this repo a configuration/acceptance-test pilot.

## High-value sources for EPL

The reference project has particularly strong EPL coverage:

```text
premierleague.core
premierleague.teams
premierleague.matches
premierleague.players
premierleague.stats
footballdatauk.history
fpl.*
espn.*
pinnacle.sports
```

The Premier League feed is based on the private JSON APIs powering premierleague.com and exposes underlying Opta data. Football-Data.co.uk is useful for historical closing prices.

## Consumer config

After the core implementation exists:

```python
SPORTSDATA = {
    "enabled": True,
    "groups": [
        "premierleague.core",
        "premierleague.teams",
        "premierleague.matches",
        "premierleague.players",
        "premierleague.stats",
        "footballdatauk.history",
        "espn.*",
        "pinnacle.sports",
    ],
    "official_provider": "premierleague",
    "fallback_provider": "espn",
}
```

## Add consumer acceptance tests only

```python
def test_epl_manifest_identifies_epl_provider_set(manifest):
    assert manifest["league"] == "epl"
    assert "premierleague.matches" in manifest["provider_groups"]


def test_epl_artifacts_not_built_for_other_league(manifest):
    assert manifest["league"] not in {"laliga", "bundesliga", "eredivisie"}
```

## Feature opportunities

Once core normalizes official data:

```text
Opta team form
lineups
match events
team/player season stats
official fixture state
historical closing odds
market dispersion/movement
FPL ownership/form as optional public-expectations research
```

FPL data should be experimental and separately tagged; fantasy ownership is not an objective player-quality metric.

## Release plan

1. Add provider support to core.
2. Cut an immutable core release.
3. Update this repo's pin.
4. Run the existing full artifact pipeline.
5. Compare old/new feature and prediction manifests.
6. Shadow market-derived features before allowing them into recommendations.

## Bottom line

Use EPL as the first soccer pilot because the reference MCP has a dedicated official-style Premier League source. Keep all reusable code in `pitch-oracle-core`.
