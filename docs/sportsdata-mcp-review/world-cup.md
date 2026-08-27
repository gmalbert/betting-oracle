# `world-cup` — SportsData MCP Review

## P0: archive the actual 2026 tournament state

The README still describes a **pre-tournament** state, an approximate hard-coded group fallback, and demo odds. As of this review (August 2026), the 2026 World Cup is complete. The first improvement should be to turn this repo into an authoritative completed-tournament archive plus reusable future-tournament pipeline.

Remove production dependence on:

```text
approximate WC2026_GROUPS
illustrative/demo odds when a real provider is unavailable
pre-tournament countdown assumptions
```

In production, missing odds should be `MARKET_UNAVAILABLE`, not invented numbers.

## MCP opportunities

```text
espn.*
apisports.*        # verify football/World Cup coverage with your key
balldontlie.*      # retain existing FIFA path separately unless verified through MCP
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

Use MCP primarily as a schedule/results/market fallback and provider-health layer.

## P0: tournament snapshot manifest

```python
@dataclass(frozen=True)
class TournamentSnapshot:
    tournament: str
    generated_at: datetime
    fixtures_complete: bool
    results_complete: bool
    standings_complete: bool
    knockout_bracket_complete: bool
    sources: dict[str, str]
```

Create a frozen archive:

```text
data_files/archive/2026/
  matches.parquet
  groups.parquet
  knockout.parquet
  team_stats.parquet
  market_snapshots.parquet
  provider_manifest.json
```

## P1: actual market history

If historical odds are available from your providers, join them to each match and preserve source semantics. Never substitute current/future reconstructed prices.

Useful post-tournament analysis:

```text
model Brier/log loss vs market
calibration by stage
model vs market upset identification
CLV where timestamped snapshots exist
tournament simulation calibration
champion probability trajectory by round
```

## P1: generic tournament engine

Refactor 2026-specific structure into data:

```python
@dataclass(frozen=True)
class TournamentFormat:
    group_count: int
    teams_per_group: int
    direct_qualifiers_per_group: int
    best_third_qualifiers: int
```

The simulator should consume a bracket definition rather than hard-coded group labels.

## P2: reproducible snapshot command

```bash
python scripts/archive_tournament.py --competition world-cup --year 2026 --strict
```

Strict mode should fail if:

```text
any game lacks a final state
knockout progression is inconsistent
provider team ids are unresolved
standings do not reconcile with group results
```

## Tests

```python
def test_no_demo_odds_in_production(): ...
def test_2026_archive_has_all_final_matches(): ...
def test_knockout_winners_advance_consistently(): ...
def test_simulator_reads_format_not_hardcoded_2026_groups(): ...
```

## Bottom line

The most important change is temporal correctness: move the repo from its old pre-event assumptions to a verified completed 2026 dataset, then use MCP as one of several provider/market sources for the reusable tournament framework.
