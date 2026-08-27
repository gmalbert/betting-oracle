# Shared SportsData Gateway

This is the highest-leverage change in the portfolio. The objective is to make `sportsdata-mcp` an **optional deterministic provider layer** behind a stable Python interface used by all sport repos.

## Design goals

- Keep each model's strongest native source as primary.
- Use MCP for secondary/fallback/enrichment/market data.
- Never require an LLM to fetch production data.
- Never expose real-money placement tools.
- Persist raw observations before normalization.
- Record provenance and timestamps for every provider-derived feature.
- Make the integration removable: if MCP is unavailable, core model pipelines still work.

## Suggested package layout

A good home is `pitch-oracle-core` only for soccer-specific code. For true portfolio-wide reuse, create a tiny package/repo such as `betting-oracle-data` or copy this module initially into the higher-value repos before extracting it.

```text
sports_gateway/
  __init__.py
  client.py
  models.py
  normalize.py
  health.py
  cache.py
  odds.py
  identity.py
  cli.py
  providers/
    mlb.py
    nba.py
    nhl.py
    espn.py
    football.py
    f1.py
    cricket.py
    tennis.py
```

## Canonical schemas

```python
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class ProviderObservation(BaseModel):
    provider: str
    capability: str
    tool: str
    fetched_at: datetime
    event_id: str | None = None
    entity_id: str | None = None
    payload: dict[str, Any]
    source_timestamp: datetime | None = None
    is_live: bool = False
    freshness_seconds: int | None = None
    request_fingerprint: str


class MarketQuote(BaseModel):
    sport: str
    league: str
    event_key: str
    bookmaker: str
    market: Literal[
        "moneyline", "spread", "total", "prop", "outright", "exchange"
    ]
    selection: str
    line: float | None = None
    decimal_odds: float
    observed_at: datetime
    provider: str
    provider_event_id: str | None = None
    provider_market_id: str | None = None
    is_live: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class ProviderHealth(BaseModel):
    provider: str
    checked_at: datetime
    status: Literal[
        "ok", "degraded", "blocked", "auth_required", "quota_exhausted", "error"
    ]
    latency_ms: float | None = None
    message: str | None = None
```

## Transport choice

The reference server supports stdio and HTTP. For local development and scheduled pipelines, prefer a **local subprocess/stdio** integration when practical. If using HTTP, bind only to `127.0.0.1` because the server's HTTP endpoint is unauthenticated.

A simple production pattern is:

```text
GitHub Action / local pipeline
        |
        +--> start sportsdata-mcp on localhost
        |
        +--> run Python ingestion
        |
        +--> stop server
```

Do not expose the HTTP transport publicly.

## Minimal MCP client wrapper

The exact MCP client import can vary by library version; isolate it behind your own interface.

```python
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


class SportsDataGateway:
    def __init__(self, session):
        self._session = session

    async def call(self, name: str, **arguments: Any) -> Any:
        result = await self._session.call_tool(name, arguments)
        return self._decode(result)

    async def call_many(self, calls: Iterable[ToolCall]) -> list[Any]:
        return await asyncio.gather(
            *(self.call(c.name, **c.arguments) for c in calls),
            return_exceptions=False,
        )

    async def tools_for_capability(self, capability: str) -> list[dict[str, Any]]:
        result = await self.call(
            "list_tools_by_capability",
            capability=capability,
        )
        return result if isinstance(result, list) else result.get("tools", [])

    @staticmethod
    def _decode(result: Any) -> Any:
        # Keep this permissive because MCP client libraries represent content
        # differently. Normalize exactly once here.
        if isinstance(result, (dict, list, str, int, float, bool)) or result is None:
            return result
        if hasattr(result, "content"):
            content = result.content
            if len(content) == 1 and hasattr(content[0], "text"):
                text = content[0].text
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
            return [getattr(x, "text", str(x)) for x in content]
        return result
```

## Subprocess launcher

```python
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def open_sportsdata(groups: str):
    env = os.environ.copy()
    env["SPORTSDATA_MCP_GROUPS"] = groups
    env["SPORTSDATA_MCP_CACHE_TTL"] = "30"

    params = StdioServerParameters(
        command="sportsdata-mcp",
        args=["serve"],
        env=env,
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield SportsDataGateway(session)
```

Usage:

```python
import asyncio


async def main():
    async with open_sportsdata("espn.*,mlb.*,pinnacle.sports") as sd:
        games = await sd.call(
            "espn_scoreboard",
            sport="baseball",
            league="mlb",
        )
        print(games)


if __name__ == "__main__":
    asyncio.run(main())
```

## Data provenance

Every normalized output should preserve:

```python
PROVENANCE_COLUMNS = [
    "source_provider",
    "source_tool",
    "source_event_id",
    "source_market_id",
    "observed_at",
    "source_timestamp",
    "request_fingerprint",
]
```

A deterministic request fingerprint:

```python
import hashlib
import json


def request_fingerprint(tool: str, arguments: dict) -> str:
    canonical = json.dumps(
        {"tool": tool, "arguments": arguments},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
```

## Immutable market snapshot writer

```python
from __future__ import annotations

from pathlib import Path
import pandas as pd


def append_market_quotes(path: str | Path, quotes: list[MarketQuote]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    new_df = pd.DataFrame([q.model_dump(mode="json") for q in quotes])
    if new_df.empty:
        return

    if path.exists():
        old = pd.read_parquet(path)
        combined = pd.concat([old, new_df], ignore_index=True)
    else:
        combined = new_df

    dedupe = [
        "event_key",
        "bookmaker",
        "market",
        "selection",
        "line",
        "decimal_odds",
        "observed_at",
        "provider",
    ]
    combined = combined.drop_duplicates(subset=dedupe, keep="last")
    combined = combined.sort_values("observed_at")

    tmp = path.with_suffix(path.suffix + ".tmp")
    combined.to_parquet(tmp, index=False)
    tmp.replace(path)
```

## Consensus and de-vig helpers

```python
from __future__ import annotations

import numpy as np
import pandas as pd


def decimal_to_implied(decimal_odds: float) -> float:
    if decimal_odds <= 1:
        raise ValueError("decimal odds must be > 1")
    return 1.0 / decimal_odds


def devig_two_way(p1: float, p2: float) -> tuple[float, float]:
    total = p1 + p2
    if total <= 0:
        raise ValueError("invalid implied probabilities")
    return p1 / total, p2 / total


def robust_consensus(values: pd.Series) -> float:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    # Median is intentionally robust to stale/bad books.
    return float(clean.median())


def market_dispersion(values: pd.Series) -> float:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if len(clean) < 2:
        return float("nan")
    return float(np.nanstd(clean, ddof=1))
```

## As-of selection — critical for leakage safety

```python
import pandas as pd


def quotes_as_of(
    quotes: pd.DataFrame,
    event_key: str,
    cutoff: pd.Timestamp,
) -> pd.DataFrame:
    q = quotes.loc[
        (quotes["event_key"] == event_key)
        & (pd.to_datetime(quotes["observed_at"], utc=True) <= cutoff)
    ].copy()
    if q.empty:
        return q

    q["observed_at"] = pd.to_datetime(q["observed_at"], utc=True)
    return (
        q.sort_values("observed_at")
         .groupby(["bookmaker", "market", "selection", "line"], dropna=False)
         .tail(1)
    )
```

Never use `latest quote in database` during historical feature generation. Always pass an explicit cutoff timestamp.

## Provider health handling

Do not convert provider errors into empty dataframes.

```python
class ProviderUnavailable(RuntimeError):
    pass


async def safe_call(sd, tool: str, **kwargs):
    try:
        payload = await sd.call(tool, **kwargs)
    except Exception as exc:
        raise ProviderUnavailable(f"{tool}: {exc}") from exc

    if payload in (None, ""):
        raise ProviderUnavailable(f"{tool}: empty response")

    return payload
```

Persist health separately:

```json
{
  "provider": "pinnacle",
  "checked_at": "2026-08-27T20:00:00Z",
  "status": "ok",
  "latency_ms": 318,
  "message": null
}
```

## Identity registry

All repos should converge on stable internal entity ids rather than joining on display names.

```python
from dataclasses import dataclass, field


@dataclass
class EntityIdentity:
    canonical_id: str
    canonical_name: str
    aliases: set[str] = field(default_factory=set)
    provider_ids: dict[str, str] = field(default_factory=dict)
```

Suggested stored table:

```text
canonical_id,entity_type,canonical_name,provider,provider_id,alias,valid_from,valid_to
```

This is especially valuable for tennis, soccer, boxing, darts, and horse racing.

## CI smoke test

Add a low-cost scheduled job that tests only the providers each repo uses.

```yaml
name: Sports data provider smoke test

on:
  workflow_dispatch:
  schedule:
    - cron: "17 11 * * *"

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install sportsdata-mcp
      - name: Provider coverage
        env:
          SPORTSDATA_MCP_GROUPS: "espn.*,pinnacle.sports"
        run: sportsdata-mcp coverage
```

For keyed providers, add only the exact secrets needed by that repo.

## Suggested dependency policy

Pin a tested minor version rather than floating indefinitely:

```text
sportsdata-mcp>=0.31,<0.32
```

Upgrade deliberately after:

1. `sportsdata-mcp lint`
2. `sportsdata-mcp doctor`
3. repo-specific fixture tests
4. schema snapshot tests
5. one shadow pipeline run

## Security boundary

Use an allowlist of groups. Never configure `all` in production.

Example:

```bash
SPORTSDATA_MCP_GROUPS="espn.*,mlb.*,pinnacle.sports"
```

Avoid account/bet-placement groups entirely. The model process should have no sportsbook login credentials.

## Optional reverse integration: Betting Oracle MCP

A small read-only MCP server would make your own portfolio queryable by AI clients.

Suggested tools:

```text
list_sports()
get_today_picks(sport=None, tier=None)
get_model_performance(sport)
get_market_snapshot(sport, event_key)
get_provider_health(sport=None)
get_model_manifest(sport)
get_prediction_explanation(sport, event_key)
```

Implementation sketch:

```python
from fastmcp import FastMCP
import json
from pathlib import Path

mcp = FastMCP("betting-oracle")

ROOT = Path(__file__).resolve().parent


@mcp.tool()
def get_today_picks(sport: str | None = None) -> list[dict]:
    rows = []
    for path in ROOT.glob("data_cache/*/best_bets_today.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if sport and payload.get("sport") != sport:
            continue
        rows.extend(payload.get("picks", []))
    return rows


if __name__ == "__main__":
    mcp.run()
```

Keep this **read-only**. It should expose research outputs, not modify models or place wagers.
