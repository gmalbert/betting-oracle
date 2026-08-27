# `boxing` — SportsData MCP Review

## Fit

KnockOutIQ's largest modeling limitation is historical fighter/fight-stat depth. The reviewed `sportsdata-mcp` catalogue does **not** solve that: UFC data is MMA, not boxing. Do not mix UFC FightMetric statistics into boxing models.

Where MCP *does* help is live and historical **market infrastructure**, especially the repo's planned sharp-line comparison.

## Recommended groups

```text
theoddsapi.*
oddsapiio.*
pinnacle.sports
espn.*              # only for boxing events actually covered
```

## P0: implement Pinnacle/sharp line through the shared market schema

```python
@dataclass(frozen=True)
class FightQuote:
    fight_id: str
    fighter_id: str
    bookmaker: str
    decimal_odds: float
    observed_at: datetime
    provider_event_id: str | None
```

Derive no-vig two-way probabilities per book:

```python
def fair_probs(a_odds, b_odds):
    pa, pb = 1/a_odds, 1/b_odds
    z = pa + pb
    return pa/z, pb/z
```

Then compare:

```text
model_prob
market_median_fair_prob
pinnacle_fair_prob
best_offered_price
market_dispersion
```

## P0: stop demo/seed limitations from contaminating model claims

Keep seed fights usable for UI development, but tag data origin:

```text
data_origin = seed | verified_historical | live_provider
```

Model training/evaluation should be able to require:

```python
train = fights[fights.data_origin == "verified_historical"]
```

## P1: line movement and CLV

```python
def clv_prob(open_or_bet_odds, closing_odds):
    return (1 / closing_odds) - (1 / open_or_bet_odds)
```

Prefer comparing no-vig probabilities or like-for-like prices rather than raw American-odds differences.

## P1: fight identity

Boxing names are notoriously inconsistent. Create provider ids and aliases:

```text
canonical_fighter_id
canonical_name
dob
boxrec_id_if_available
provider
provider_fighter_id
alias
```

Fight key should include both canonical fighter ids and scheduled date; account for reschedules.

## P2: historical data remains a separate project

Prioritize acquisition of verified historical boxing stats such as:

```text
opponent quality
rounds fought
knockdowns
method
weight class
age at fight
layoff
reach/height
stance
fight-level punch stats where legitimately available
```

MCP should not delay that work or create false confidence that it is covered.

## Tests

```python
def test_ufc_data_never_enters_boxing_model(): ...
def test_seed_data_excluded_from_production_training(): ...
def test_pinnacle_quote_is_same_fight_and_market(): ...
def test_rescheduled_fight_keeps_identity_lineage(): ...
```

## Bottom line

Use MCP to solve the market side—Pinnacle, multi-book snapshots, CLV and provenance. Continue a separate effort to deepen verified historical boxing statistics.
