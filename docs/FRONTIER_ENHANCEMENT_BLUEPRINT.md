# Frontier Enhancement Blueprint

This repository is presently a portfolio/catalog site; existing docs cover its visual redesign, project cards, feature roadmap, accessibility, and cross-sport positioning. The next useful step is a live, machine-readable research registry rather than additional static marketing sections.

## Unified project registry

Drive project pages from a validated manifest supplied by each prediction repo.

```json
{
  "project_id": "mlb",
  "status": "active",
  "artifact_url": ".../project-status.json",
  "model_version": "2026.08.1",
  "data_as_of": "2026-08-06T12:00:00Z",
  "metrics": {"log_loss": 0.61, "clv": 0.012},
  "limitations": ["lineups provisional"]
}
```

Validate manifests in CI, cache the last healthy version, and show stale/unavailable states honestly. Keep model metrics comparable by defining the evaluation window, market, odds source, and sample count.

## Research narrative

- Versioned model cards with training window, features, calibration, exclusions, and known failure modes.
- Changelog showing when a model/data source changed and whether historical metrics were recomputed.
- Interactive “how a probability becomes a decision” explainer using a synthetic example.
- Cross-project data-source map and freshness dashboard.
- Reproducible methodology downloads and schema links.

## UI additions

- Filterable project matrix by sport, season, operational health, and model maturity.
- Side-by-side project comparison with normalized metrics and sample-size warnings.
- Accessibility-first charts with downloadable tables and reduced-motion mode.
- Status badge sourced from data, not manually edited HTML.
- Clear separation between research results, live picks, and archived experiments.

## Governance

Add automated broken-link, schema, accessibility, and stale-status checks. Every displayed performance claim must link to a versioned artifact. Never aggregate ROI across incompatible units or time windows. Publish responsible-use limits and make uncertainty/failure states prominent.
