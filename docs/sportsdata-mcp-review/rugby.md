# `rugby` — SportsData MCP Review

## Best fit: consolidate a five-source scraping/API stack

ScrumBet currently uses ESPN, RugbyPass, SofaScore, World Rugby and The Odds API across six competitions. The reference MCP's keyed `apisports` provider is notable because its catalogue identifies it as the rugby-union coverage path.

Important caveat: the reference project explicitly says keyed-provider response shapes were documented rather than live-verified by its maintainer. Treat `apisports` as a **shadow source until your own key passes contract tests**.

## Recommended groups

```text
apisports.*
espn.*
theoddsapi.*
oddsapiio.*
pinnacle.sports
```

## P0: competition-by-provider coverage matrix

```text
data_files/provider_coverage.parquet

competition
provider
fixtures
results
standings
players
odds
last_verified_at
status
```

Example:

```python
REQUIRED = {
    "six_nations": {"fixtures", "results"},
    "premiership": {"fixtures", "results", "standings"},
    "top14": {"fixtures", "results", "standings"},
}
```

A provider should not become primary for a competition until every required capability has a passing sample fixture.

## P0: normalized match schema

```python
@dataclass
class RugbyMatch:
    match_id: str
    competition: str
    kickoff_utc: datetime
    home_team_id: str
    away_team_id: str
    home_score: int | None
    away_score: int | None
    status: str
    provider_ids: dict[str, str]
```

Preserve SofaScore/ESPN provider ids instead of rematching names nightly.

## P1: odds snapshots

Store moneyline and total observations from all available providers in the shared quote ledger. For three-way markets, preserve draw pricing if offered; do not force every competition into a two-way structure.

```python
def devig_three_way(odds):
    p = [1 / x for x in odds]
    z = sum(p)
    return [x / z for x in p]
```

## P1: try-scorer props

The current try-scorer model would benefit from line history before expanding recommendation logic.

Canonical contract:

```text
match_id
player_id
market=anytime_try
bookmaker
price
observed_at
```

Evaluate the probability model with Brier/log loss and realized EV, not only classification accuracy.

## P2: source fallback policy

```python
SOURCE_POLICY = {
    "live_scores": ["sofascore", "espn"],
    "official_rankings": ["world_rugby"],
    "fixtures": ["apisports", "espn", "rugbypass"],
    "odds": ["sportsdata_multi_book", "existing_odds_api"],
}
```

Do not remove the World Rugby source merely because a generic provider also has rankings.

## Tests

```python
def test_apisports_shape_verified_before_primary_use(): ...
def test_draw_market_not_collapsed_to_two_way(): ...
def test_competition_provider_coverage_gate(): ...
def test_try_scorer_quote_precedes_prediction(): ...
```

## Bottom line

Rugby is a good candidate for source consolidation, but keyed API-Sports data should enter shadow validation first. The strongest immediate win is a competition coverage matrix and multi-book market ledger.
