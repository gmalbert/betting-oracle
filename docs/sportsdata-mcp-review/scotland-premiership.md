# `scotland-premiership` — SportsData MCP Review

## Recommendation

Keep this repo thin and implement the actual MCP adapter in `pitch-oracle-core`. Scotland already has Odds-API.io configuration, so the immediate benefit is to put that provider behind the same shared contract as ESPN/football-data history.

## Candidate groups

```text
espn.*
footballdataorg.*
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

Coverage is the gate: confirm Scottish Premiership competition support with `sportsdata-mcp coverage` from the actual CI/deployment location.

## Consumer config

```python
SPORTSDATA = {
    "enabled": True,
    "groups": ["espn.*", "footballdataorg.*", "oddsapiio.*"],
    "odds_sources": ["oddsapiio", "existing"],
    "min_market_books": 2,
}
```

## Improve the existing bookmaker config

Instead of a comma-separated env var being the only contract, persist what was actually observed:

```json
{
  "requested_books": ["Bet365", "Unibet"],
  "returned_books": ["Bet365"],
  "observed_at": "2026-08-27T20:00:00Z",
  "provider": "oddsapiio",
  "status": "partial"
}
```

This prevents “one book returned” from looking like consensus.

## Acceptance tests

```python
def test_manifest_league_is_scottish_premiership(...): ...
def test_requested_books_not_assumed_returned(...): ...
def test_odds_provider_partial_state_visible(...): ...
def test_core_pin_matches_workflow_ref(...): ...
```

## Bottom line

No duplicated integration code here. Let core own MCP and use this consumer to validate real Scottish coverage and market completeness.
