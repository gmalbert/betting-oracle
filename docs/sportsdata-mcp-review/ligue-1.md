# `ligue-1` — SportsData MCP Review

## Fit

This repo is already one of the stronger soccer implementations: append-only market snapshots, multiple model families, API-Football enrichment, quota guards, market baseline evaluation and nightly artifacts. MCP should **consolidate provider plumbing and add fallback**, not create a second parallel snapshot system.

## Recommended groups

```text
espn.*
footballdatauk.history
footballdataorg.*
apisports.*          # only after live shape verification with your key
sportmonks.*         # optional enrichment
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

## P0: feed MCP quotes into the existing market ledger

Do not create `market_snapshots_v2`. Implement one adapter producing the repo's existing quote schema.

```python
class SportsDataOddsAdapter:
    def normalize(self, provider_payload) -> list[CanonicalQuote]:
        ...
```

Every row should retain `source_provider`, `provider_event_id`, `provider_market_id`, and `observed_at`.

## P1: replace quota-specific branches with provider state

```python
@dataclass
class ProviderState:
    provider: str
    available: bool
    quota_remaining: int | None
    verified_shape: bool
    last_success: datetime | None
    error: str | None
```

Feature generation should depend on **capability availability**, not “API-Football worked today.”

## P1: historical closing-odds benchmark

Use `footballdatauk.history` to augment the existing backtest with a consistent closing-price baseline where league/season coverage overlaps.

```text
our_model_logloss
market_closing_logloss
hybrid_logloss
flat_stake_roi_at_observed_quote
clv_vs_closing
```

## P1: provider agreement features

Since the repo already stores snapshots, add:

```python
features["odds_book_count"] = quotes.bookmaker.nunique()
features["spread_of_home_prob"] = quotes.home_no_vig_prob.std()
features["median_home_prob"] = quotes.home_no_vig_prob.median()
features["best_price_edge"] = best_price_prob - features["median_home_prob"]
```

## P2: migrate shared behavior to core

The repo's source-state and nightly-market patterns are good candidates to upstream into `pitch-oracle-core` so thinner consumers inherit them.

## Tests

```python
def test_mcp_adapter_writes_existing_quote_contract(): ...
def test_unverified_keyed_provider_cannot_enter_model_features(): ...
def test_quota_exhaustion_is_not_empty_fixture_list(): ...
def test_closing_odds_join_is_season_and_match_safe(): ...
```

## Bottom line

This repo needs integration discipline more than new features. Reuse its mature snapshot architecture and let MCP widen/standardize the source pool.
