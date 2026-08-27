# `portugal-soccer` — SportsData MCP Review

## Recommendation

Keep this repo as a thin Primeira Liga consumer. Implement MCP support once in `pitch-oracle-core`, then enable providers here only after live coverage validation.

## Candidate groups

```text
espn.*
footballdataorg.*
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

## Config

```python
SPORTSDATA = {
    "enabled": True,
    "groups": ["espn.*", "footballdataorg.*", "oddsapiio.*"],
    "fixture_sources": ["football_data_org", "espn"],
    "odds_sources": ["oddsapiio", "existing"],
}
```

## P0: make optional-source semantics explicit

The current consumer docs correctly say optional sources should only be added after coverage/failure-mode tests. Codify that in the artifact manifest:

```json
{
  "optional_sources": {
    "sportsdata": {
      "required": false,
      "coverage_verified": true,
      "last_success": "...",
      "status": "ready"
    }
  }
}
```

A failed optional provider should not invalidate a sound sports-only cache unless its features were required by the trained model.

## P1: odds consensus and movement

Once core supplies the shared quote ledger, enable:

```text
1x2 no-vig median
book dispersion
best-vs-median price
opening/current movement
quote freshness
book count
```

## Tests

```python
def test_manifest_league_is_primeira_liga(...): ...
def test_optional_provider_failure_semantics(...): ...
def test_market_features_require_snapshot_id(...): ...
def test_consumer_core_pin_matches_artifact(...): ...
```

## Bottom line

This repo needs almost no bespoke MCP code. Let the shared core own it and use Portugal-specific coverage/failure tests as the gate.
