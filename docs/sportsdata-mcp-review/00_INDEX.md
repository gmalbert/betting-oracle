# Sportsdata MCP Portfolio Review

**Reviewed:** 2026-08-27  
**Reference project:** `DanielTomaro13/sportsdata-mcp` (v0.31.1 at review time)  
**Scope:** Sports/betting repositories under `gmalbert`

## Executive summary

`sportsdata-mcp` should **not** replace the strongest native sources already used by the Betting Oracle projects (NFLverse, CFBD, FastF1/F1DB, Cricsheet, American Soccer Analysis, etc.). Its highest-value role is a **shared enrichment, market-data, source-fallback, and research gateway**.

The biggest portfolio-wide opportunities are:

1. **One provider gateway for every repo.** Add a small `SportsDataGateway` wrapper around the MCP server so apps do not each maintain separate ESPN/Pinnacle/official-league HTTP quirks.
2. **Cross-book consensus and sharp-line features.** Use Pinnacle, FanDuel, prediction markets, and any legally/reliably reachable provider to create consensus, dispersion, movement, and sharp-vs-retail features.
3. **Immutable market snapshots.** Every prediction repo should write timestamped odds snapshots before games. This unlocks honest CLV, line-movement, closing-line benchmarking, and time-aware backtesting.
4. **Provider provenance and health.** Persist source, tool, fetched-at, request fingerprint, freshness, and failure reason next to every external datum.
5. **Official-source fallbacks.** MLB, NHL, NBA, Premier League, La Liga, F1, cricket, WTA, and NCAA all gain useful official/public fallback paths.
6. **Provider capability discovery instead of hard-coding.** `sportsdata-mcp` tags tools by capability. Build portfolio logic around capabilities such as `sport.fixtures_by_date`, `sport.event_markets`, `stats.ladder`, etc.
7. **Expose Betting Oracle back to AI tools.** A small read-only Betting Oracle MCP server can expose your own `best_bets_today.json`, model manifests, performance, and source-health data to ChatGPT/Cursor/Claude without giving an agent write or bet-placement access.
8. **Never enable real-money bet-placement tool groups in model-training or dashboard processes.** The reference project contains real-money placement tools for some Australian books. Keep the Betting Oracle integration strictly read-only.

## Recommended implementation order

### P0 — shared infrastructure

- Implement [`01_SHARED_GATEWAY.md`](01_SHARED_GATEWAY.md).
- Add a canonical `MarketQuote` / `ProviderObservation` schema.
- Add provider-health and provenance storage.
- Add a CLI smoke check for the exact groups each repo depends on.

### P1 — projects with immediate high-value gains

1. [`college-football-predictions.md`](college-football-predictions.md) — multi-book immutable snapshots directly address the repo's stated missing CLV history.
2. [`golf-predictions.md`](golf-predictions.md) — DataGolf is an unusually strong fit and can replace several brittle scraping paths.
3. [`horse-racing-predictions.md`](horse-racing-predictions.md) — real market odds are the biggest missing ingredient in the current backtester.
4. [`tennis-predictions.md`](tennis-predictions.md) — WTA official data + alternate odds providers can reduce RapidAPI dependency.
5. [`hockey-predictions.md`](hockey-predictions.md) — official NHL depth + ESPN + odds consensus can strengthen goalie/injury/market layers.
6. [`baseball-predictions.md`](baseball-predictions.md) — comprehensive MLB Stats API wrapper and market-source redundancy.
7. [`nba-predictions.md`](nba-predictions.md) and [`wnba-predictions.md`](wnba-predictions.md) — direct NBA stats/CDN access, ESPN fallbacks, player-prop enrichment.

### P2 — shared soccer stack

Implement the adapter once in [`pitch-oracle-core.md`](pitch-oracle-core.md), then enable it per consumer:

- [`premier-league.md`](premier-league.md)
- [`la-liga.md`](la-liga.md)
- [`bundesliga.md`](bundesliga.md)
- [`ligue-1.md`](ligue-1.md)
- [`mls-predictions.md`](mls-predictions.md)
- [`netherlands-soccer.md`](netherlands-soccer.md)
- [`scotland-premiership.md`](scotland-premiership.md)
- [`belgium-soccer.md`](belgium-soccer.md)
- [`turkey-soccer.md`](turkey-soccer.md)
- [`portugal-soccer.md`](portugal-soccer.md)
- [`world-cup.md`](world-cup.md)

### P3 — other sport apps

- [`f1Analysis.md`](f1Analysis.md)
- [`nfl-predictions.md`](nfl-predictions.md)
- [`march-madness.md`](march-madness.md)
- [`rugby.md`](rugby.md)
- [`cricket.md`](cricket.md)
- [`darts.md`](darts.md)
- [`boxing.md`](boxing.md)
- [`table-tennis.md`](table-tennis.md)

### Portfolio presentation/aggregation

- [`betting-oracle.md`](betting-oracle.md)
- [`sports-picks-grid.md`](sports-picks-grid.md)

## What not to do

- Do not route every production request through an LLM just because the source is exposed through MCP. The MCP server should be treated as a deterministic data service.
- Do not use a live market quote as a training feature unless the timestamp proves it existed at prediction time.
- Do not silently merge conflicting provider values. Preserve every observation and derive consensus explicitly.
- Do not use geographically blocked Australian-book responses as if they were missing markets.
- Do not let an empty provider response mean "no games" unless the provider health check confirms success.
- Do not add betting-placement credentials to Streamlit Cloud, GitHub Actions, or model-training environments.

## Suggested new shared artifacts

Every sports repo should eventually be able to emit these files:

```text
data_files/
  provider_health.json
  source_manifest.json
  market_snapshots.parquet
  market_consensus.parquet
  best_bets_today.json
  model_performance.json
  model_manifest.json
```

That gives `sports-picks-grid` and the Betting Oracle hub a stable contract across every sport.
