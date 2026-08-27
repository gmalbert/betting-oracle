# `table-tennis` — SportsData MCP Review

## Fit

Pong Odds already has several good foundations: a canonical player identity map, nightly precompute, uncertainty-aware filters, explainability and Brier-score backtesting. The reviewed MCP catalogue does not expose a clearly documented dedicated table-tennis statistics provider, so MCP should initially be treated as **market infrastructure only**.

## Candidate groups

```text
oddsapiio.*
theoddsapi.*
pinnacle.sports
```

Do not assume table-tennis coverage merely because a provider supports many sports. Probe the provider catalogue and `sportsdata-mcp coverage` first.

## P0: extend the existing identity map with provider ids

```text
canonical_player_id
canonical_name
provider
provider_player_id
alias
last_verified_at
```

```python
def attach_provider_id(identity_df, canonical_id, provider, provider_id):
    row = {
        "canonical_player_id": canonical_id,
        "provider": provider,
        "provider_player_id": str(provider_id),
        "last_verified_at": pd.Timestamp.utcnow(),
    }
    return pd.concat([identity_df, pd.DataFrame([row])], ignore_index=True)
```

## P0: immutable upcoming-market snapshots

The nightly `upcoming_enriched.json` is optimized for serving, but it should not be the historical market ledger. Add:

```text
processed/market_snapshots.parquet
```

with:

```text
match_key
player1_id
player2_id
bookmaker
selection_player_id
decimal_odds
observed_at
provider_market_id
```

## P1: confidence should include data coverage

You already expose coverage tier/sample size. Make recommendation eligibility explicit:

```python
def recommendation_gate(model_prob, market_prob, sample_n, source_count):
    edge = model_prob - market_prob
    if sample_n < 20:
        return "ABSTAIN_LOW_SAMPLE"
    if source_count < 1:
        return "ABSTAIN_NO_MARKET"
    if edge < 0.04:
        return "NO_EDGE"
    return "CANDIDATE"
```

If several books become available, require a minimum consensus book count rather than `source_count >= 1`.

## P1: line-movement feature

```python
def probability_move(old_odds, new_odds):
    return 1/new_odds - 1/old_odds
```

Measure movement only across quotes for the same match/player/book/market.

## P2: discover, don't hard-code

Build a small nightly capability probe:

```python
async def table_tennis_market_capability(sd):
    tools = await sd.tools_for_capability("sport.event_markets")
    return [t for t in tools if "odds" in t.get("provider", "").lower()]
```

Then test actual sport coverage before invoking expensive event calls.

## Tests

```python
def test_provider_player_ids_do_not_replace_canonical_ids(): ...
def test_market_snapshot_is_append_only(): ...
def test_low_sample_prediction_abstains(): ...
def test_missing_table_tennis_provider_is_explicit(): ...
```

## Bottom line

Pong Odds is already architecturally cleaner than many small-sport projects. Use MCP to improve odds provenance and history, but do not claim a new statistics source until live coverage is verified.
