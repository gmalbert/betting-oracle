# `bundesliga` — SportsData MCP Review

## P0: fix the repository identity/documentation before adding data

The current README appears to be copied from the La Liga project: it is titled **La Liga Linea**, clones `gmalbert/la-liga`, uses La Liga competition codes, and describes Copa del Rey/Spanish-specific behavior. That creates a real operational risk because a contributor or automation can follow valid-looking instructions for the wrong league.

Before any MCP integration:

```text
- rename README title/branding to Bundesliga
- correct clone URL and directory
- correct competition/source codes
- remove La Liga-specific cup notes
- verify .env examples and nightly workflow league ids
- add a test asserting configured league == bundesliga
```

Example guard:

```python
def test_repository_league_identity():
    from config import LEAGUE_KEY
    assert LEAGUE_KEY == "bundesliga"
```

## Strong MCP fit: OpenLigaDB

The reference project includes `openligadb.football` with Bundesliga 1/2/3 and DFB-Pokal fixtures, results, tables and matchdays.

Recommended groups:

```text
openligadb.football
espn.*
footballdatauk.history
theoddsapi.*
pinnacle.sports
```

## P1: source hierarchy

```python
BUNDESLIGA_SOURCES = {
    "fixtures": ["openligadb", "espn", "football_data_org"],
    "standings": ["openligadb", "espn"],
    "history_odds": ["footballdatauk"],
    "live_odds": ["pinnacle", "existing_odds"],
}
```

OpenLigaDB is crowd-maintained, so it should be validated against a second source rather than treated as infallible.

## P1: match-result parsing contract

The reference notes that OpenLigaDB stores multiple result entries such as half-time and full-time. Normalize explicitly:

```python
def full_time_result(match_results):
    candidates = [r for r in match_results if r.get("resultTypeID") == 2]
    if len(candidates) != 1:
        raise ValueError(f"expected one FT result, got {len(candidates)}")
    return candidates[0]
```

Do not use `matchResults[0]`.

## P1: migrate toward `pitch-oracle-core`

Once the README/config identity is repaired, this repo is an excellent candidate to become a thin core consumer. Add the MCP implementation to core and keep only Bundesliga source selection/config here.

## Tests

```python
def test_readme_and_config_name_same_league(): ...
def test_openligadb_selects_full_time_result(): ...
def test_bundesliga_provider_does_not_accept_laliga_ids(): ...
def test_df_pokal_matches_not_mixed_into_league_training_without_flag(): ...
```

## Bottom line

The immediate improvement is not modeling—it is fixing the repo's La Liga copy artifacts. Then use OpenLigaDB as a free Bundesliga-specific source through the shared core adapter.
