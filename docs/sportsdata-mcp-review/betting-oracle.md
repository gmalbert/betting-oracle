# `betting-oracle` — SportsData MCP Review

## Evolve the hub from hand-maintained cards into a portfolio control plane

The current repo is a useful landing page, but its descriptions and shared footer are manually maintained. With dozens of betting projects, this repo is the right place to publish a **machine-readable portfolio registry, model/status rollup, provider-health view, shared schema documentation, and optional read-only MCP server**.

## P0: portfolio registry

Create:

```text
portfolio/repos.yaml
```

Example:

```yaml
schema_version: 1
repos:
  - id: nfl
    repo: gmalbert/nfl-predictions
    name: Gridiron Oracle
    sport: football
    league: NFL
    app_url: https://www.gridiron-oracle.com
    picks: data_files/best_bets_today.json
    performance: data_files/model_performance.json
    health: data_files/provider_health.json
    active: true

  - id: f1
    repo: gmalbert/f1Analysis
    name: Gridlocked Oracle
    sport: motorsport
    league: Formula 1
    picks: data_files/best_bets_today.json
    active: true
```

Generate the README/cards from this registry instead of editing duplicated prose.

```python
import yaml
from pathlib import Path

registry = yaml.safe_load(Path("portfolio/repos.yaml").read_text())
for repo in registry["repos"]:
    print(repo["name"], repo["repo"])
```

## P0: shared schema contracts

Move portfolio-wide JSON contracts here or to a tiny package:

```text
schemas/
  best_bets.schema.json
  model_performance.schema.json
  provider_health.schema.json
  model_manifest.schema.json
```

Example health schema shape:

```json
{
  "schema_version": 1,
  "generated_at": "...",
  "providers": [
    {
      "provider": "espn",
      "status": "ok",
      "last_success": "...",
      "latency_ms": 244,
      "message": null
    }
  ]
}
```

Each sport repo validates exports against these contracts in CI.

## P0: stop copying `footer.py`

The current README recommends copying a footer into every app. That guarantees drift. Prefer a shared package/component.

Minimal package approach:

```python
# betting_oracle_ui/footer.py
import streamlit as st


def render_footer(app_name: str | None = None):
    label = f"{app_name} · Betting Oracle" if app_name else "Betting Oracle"
    st.markdown(
        f"""
        <div class="bo-footer">
          <a href="https://www.betting-oracle.com" target="_blank">{label}</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
```

Then pin it in consumers. If a package is too much initially, at least keep one raw GitHub source with a version/hash check instead of copy/paste divergence.

## P1: generated portfolio status page

Aggregate the standardized artifacts:

```text
App              Model   Data       Market      Last build
Gridiron Oracle  READY   READY      6 books     18m
Equine Edge      READY   READY      DEGRADED    1h
Gridlocked       READY   READY      3 books     42m
Wicket Oracle    READY   READY      4 books     27m
```

Separate:

```text
MODEL STATUS
DATA STATUS
MARKET STATUS
DEPLOYMENT STATUS
```

A model can be healthy while its live market data is degraded.

## P1: read-only Betting Oracle MCP server

This is a creative use of the reference project in the opposite direction: expose **your own portfolio outputs** to AI clients.

Suggested package:

```text
betting_oracle_mcp/
  server.py
  registry.py
  loaders.py
  schemas.py
```

Tools:

```text
list_apps()
get_today_picks(sport=None, tier=None)
get_event_prediction(sport, event_key)
get_model_performance(sport)
get_provider_health(sport=None)
get_model_manifest(sport)
compare_sports_models()
```

Example:

```python
from fastmcp import FastMCP
from pathlib import Path
import json

mcp = FastMCP("betting-oracle")
CACHE = Path("data_cache")


@mcp.tool()
def get_today_picks(sport: str | None = None, tier: str | None = None):
    output = []
    for file in CACHE.glob("*/best_bets_today.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        for pick in data.get("picks", []):
            if sport and pick.get("sport") != sport:
                continue
            if tier and pick.get("tier") != tier:
                continue
            output.append(pick)
    return output


@mcp.tool()
def get_provider_health(sport: str | None = None):
    rows = []
    for file in CACHE.glob("*/provider_health.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        if sport and data.get("sport") != sport:
            continue
        rows.append(data)
    return rows
```

### Security rule

This MCP server must remain **read-only**. It should never:

```text
place bets
store sportsbook credentials
trigger retraining
modify repositories
write bankroll state
```

It is a research/query surface only.

## P1: central source catalog

Document every upstream source once:

```text
provider
sports/leagues
cost/key
geo restrictions
primary repos
fallback repos
historical depth
market history available?
known failure semantics
last validated
```

This prevents five repos independently rediscovering that an endpoint changed or a free tier no longer covers a season.

## P1: provider version/change watch

`sportsdata-mcp` itself supports signed spec overlays because external endpoints drift. Track the version used to build each artifact:

```json
{
  "sportsdata_mcp": "0.31.1",
  "provider_specs": {
    "espn": "packaged",
    "pinnacle": "overlay:2026-08-27"
  }
}
```

A cross-portfolio report can then identify which apps need revalidation after an MCP upgrade.

## P2: portfolio-wide model governance

Create a standard release gate:

```python
@dataclass(frozen=True)
class ModelReleaseGate:
    leakage_checks: bool
    walk_forward_oos: bool
    calibration_report: bool
    market_baseline: bool
    sample_size_reported: bool
    source_manifest: bool
    artifact_hashes: bool
```

Every app can be classified:

```text
RESEARCH
SHADOW
PAPER
PRODUCTION_RECOMMENDATIONS
```

Do not promote based solely on a headline accuracy/ROI number.

## P2: shared utilities package

Potential package modules:

```text
betting_oracle_common/
  odds.py
  markets.py
  identities.py
  artifacts.py
  health.py
  manifests.py
  schemas.py
  streamlit_ui.py
```

This would eliminate repeated American/decimal odds conversion, no-vig calculations, freshness rules, JSON formats and footer code across repos.

## P2: central CI schema check

Each repo can consume a tagged schema release:

```yaml
- name: Validate Betting Oracle exports
  run: python -m betting_oracle_common.validate_exports data_files/
```

And the hub can nightly validate every public repo output.

## Relationship to `sportsdata-mcp`

Use the external project as:

```text
upstream provider gateway  -> sport repos
                             -> normalized artifacts
                             -> Sports Picks Grid / Betting Oracle
                             -> read-only Betting Oracle MCP
```

This creates a clean separation:

- `sportsdata-mcp` knows external sports providers;
- each prediction repo knows its sport/model;
- Sports Picks Grid knows normalized recommendations;
- Betting Oracle knows the portfolio.

## Bottom line

The hub can become much more valuable without containing a single predictive model. Make it the source of truth for **portfolio identity, schemas, health, model-release state, shared utilities and AI-readable research outputs**.
