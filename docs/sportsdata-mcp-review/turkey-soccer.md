# `turkey-soccer` — SportsData MCP Review

## Strategy

This repo already uses football-data.org, ESPN and Odds-API.io and identifies itself as part of the Pitch Oracle family. Move its provider plumbing toward `pitch-oracle-core` rather than adding another standalone integration.

## Candidate groups

```text
espn.*
footballdataorg.*
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

Verify Süper Lig coverage with `sportsdata-mcp coverage` before enabling any provider in production.

## P0: source contract + league guard

```python
LEAGUE_KEY = "super_lig"

SPORTSDATA = {
    "enabled": True,
    "groups": ["espn.*", "footballdataorg.*", "oddsapiio.*"],
    "min_market_books": 2,
}
```

```python
def test_no_cross_league_artifacts(manifest):
    assert manifest["league"] == "super_lig"
```

## P1: bookmaker completeness

The UI promises bookmaker comparison, so expose whether it is actually comparing books:

```python
def market_completeness(quotes):
    return {
        "books": quotes.bookmaker.nunique(),
        "oldest_quote": quotes.observed_at.min(),
        "newest_quote": quotes.observed_at.max(),
        "complete_1x2_books": quotes.groupby("bookmaker").selection.nunique().ge(3).sum(),
    }
```

Do not show a “best bet” based on a single stale book as though it were market consensus.

## P1: market-independent benchmark

Because current odds are listed as model features, retain a sports-only model for evaluation:

```text
fundamental-only
market-only
hybrid
```

This is essential to know whether the ensemble contributes anything beyond the line.

## P2: migration

Once core gains `SportsDataFootballProvider`, update this repo to a pinned core release and remove duplicate source-client code where possible.

## Tests

```python
def test_super_lig_coverage_probe(...): ...
def test_best_bet_requires_fresh_market(...): ...
def test_fundamental_model_has_no_odds_columns(...): ...
```

## Bottom line

The improvement is not a new Turkish model; it is trustworthy multi-book data and convergence on the shared Pitch Oracle provider architecture.
