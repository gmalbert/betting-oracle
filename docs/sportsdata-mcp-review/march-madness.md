# `march-madness` — SportsData MCP Review

## Strategy

Keep CBBD, KenPom and BartTorvik. Those efficiency sources are core differentiators and are not replaced by the reference MCP. Use MCP to harden **schedule/poll/market** data and reduce dependence on scraping for facts available elsewhere.

## Recommended groups

```text
ncaa.college
espn.*
theoddsapi.*
oddsapiio.*
```

## P0: NCAA/ESPN schedule reconciliation

```python
@dataclass
class CollegeGameIdentity:
    canonical_game_id: str
    season: int
    home_team_id: str
    away_team_id: str
    tipoff_utc: datetime
    cbbd_id: str | None
    espn_id: str | None
    ncaa_id: str | None
```

Build the mapping before feature generation. Team-name canonicalization should resolve provider ids once, rather than fuzzy-match every nightly run.

## P1: poll snapshots

The NCAA provider offers AP/coaches polls. Store every poll with publication/as-of date:

```text
team_id
poll_type
rank
points
first_place_votes
published_at
source
```

Join with:

```python
polls = polls[polls.published_at <= game_prediction_time]
latest = polls.sort_values("published_at").groupby(["team_id", "poll_type"]).tail(1)
```

Potential features: rank delta, ranked-vs-unranked, poll disagreement, recent movement.

## P1: replace a single “Vegas line” with a market state

```text
spread_consensus
spread_dispersion
total_consensus
total_dispersion
moneyline_no_vig_consensus
book_count
open_to_current_spread_move
open_to_current_total_move
```

Store all quotes immutably. Tournament markets can move rapidly after injuries/bracket advancement.

## P1: stop browser scraping from being a production single point of failure

KenPom/BartTorvik still require their current acquisition paths, but isolate them as enrichment modules with explicit status:

```python
SOURCE_STATES = {
    "kenpom": "ready|stale|failed",
    "barttorvik": "ready|stale|failed",
    "cbbd": "ready|failed",
    "ncaa": "ready|failed",
    "market": "ready|partial|missing",
}
```

A browser-blocked enrichment should not erase otherwise valid game records.

## P2: selection-time model contract

March Madness needs unusually strict timestamp semantics because bracket information changes round by round.

```python
@dataclass(frozen=True)
class TournamentPredictionContract:
    game_id: str
    round_name: str
    bracket_known_at: datetime
    feature_cutoff: datetime
    market_cutoff: datetime
```

Do not let later-round opponent information enter an earlier simulation state.

## P2: simulation + market benchmark

For bracket simulations, report both model advancement probabilities and market-implied futures where available:

```text
Team        Model title%   Market fair%   Delta
Duke        18.2%          20.4%          -2.2%
Houston     13.4%          11.0%          +2.4%
```

Treat this as calibration/benchmarking before calling it value.

## Tests

```python
def test_poll_snapshot_precedes_game(): ...
def test_bracket_state_does_not_know_future_opponent(): ...
def test_market_consensus_requires_min_books(): ...
def test_scraper_failure_preserves_last_good_enrichment(): ...
```

## Bottom line

The MCP contribution is robust public schedule/poll data plus a proper multi-book market ledger. Preserve KenPom/BartTorvik and focus on point-in-time tournament state.
