# `netherlands-soccer` — SportsData MCP Review

## Recommendation

Keep this as a thin `pitch-oracle-core` consumer. Do not add MCP runtime code locally.

## Source opportunities

```text
espn.*
footballdataorg.*      # Eredivisie is specifically cited as useful coverage
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

Use `sportsdata-mcp coverage` to verify the competition/provider combination before enabling it in the artifact workflow.

## Config after core support lands

```python
SPORTSDATA = {
    "enabled": True,
    "groups": [
        "espn.*",
        "footballdataorg.*",
        "oddsapiio.*",
    ],
    "min_market_books": 2,
}
```

## Consumer-specific acceptance tests

```python
def test_manifest_is_eredivisie(manifest):
    assert manifest["league"] == "eredivisie"


def test_fixture_provider_returns_expected_club_count_or_valid_phase(...): ...
def test_artifacts_share_pinned_core_and_source_contract(...): ...
```

## Feature ideas after shared integration

- multi-book 1X2 consensus and dispersion;
- market movement;
- source-verified standings/fixtures;
- optional player/team enrichment only when timestamp-safe;
- source-health status on the app.

## Bottom line

This repo should benefit automatically from the core adapter. The main local work is source selection, secrets, and league-specific acceptance tests.
