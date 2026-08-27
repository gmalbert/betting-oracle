# `belgium-soccer` — SportsData MCP Review

## Recommendation

This is already a thin `pitch-oracle-core` consumer. Keep it that way. Add MCP provider support to core, then enable only providers whose Belgian Pro League coverage is verified.

## Candidate provider groups

```text
espn.*
footballdataorg.*
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

Do not infer coverage from a provider supporting “soccer” generally. Make the artifact workflow prove that Belgian fixtures can be fetched.

## Coverage gate

```python
@dataclass(frozen=True)
class LeagueCoverage:
    league: str
    provider: str
    fixtures_found: int
    next_fixture_at: datetime | None
    checked_at: datetime
    status: str
```

Fail artifact publication if the configured primary provider says success but returns an implausibly empty current competition while another source shows fixtures.

## Consumer config

```python
SPORTSDATA = {
    "enabled": True,
    "groups": ["espn.*", "footballdataorg.*", "oddsapiio.*"],
    "fixture_sources": ["football_data_org", "espn"],
    "odds_sources": ["oddsapiio"],
}
```

## Tests

```python
def test_manifest_league_is_belgian_pro_league(...): ...
def test_provider_coverage_is_verified_before_publish(...): ...
def test_empty_primary_checked_against_secondary(...): ...
```

## Bottom line

The improvement is shared provider resilience and market snapshots, implemented once in core and verified here with Belgian-specific coverage tests.
