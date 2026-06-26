# Betting Oracle (Portfolio Site) — Model Suggested Enhancements

## Not Applicable — Static HTML Site

The Betting Oracle site has no ML models. Enhancement suggestions apply to its aggregation and presentation layer instead.

## Priority 1: Data Aggregation Quality

### Signal Freshness Indicator
- Each sport card on the portfolio page should show how recently its `best_bets_today.json` was updated.
- Stale feeds (>24 hours) should be visually flagged with a warning colour.

### Cross-Sport Correlation Warning
- When the same underlying game is exposed through two sport apps (e.g., an MLS vs. La Liga overlap for international games), flag potential duplicate bets to avoid correlated exposure.

### Consensus Pick Aggregation
- Where multiple Betting Oracle apps cover the same sport, compute a meta-confidence score using a weighted average of individual app edge scores.

## Priority 2: Footer & Branding

### A/B Test Footer CTAs
- Test two variants of the "Powered by Betting Oracle" footer CTA: one linking to the portfolio, one linking to a specific sport app.
- Track click-through rates using a free UTM parameter strategy.

### Footer Version Stamp
- Embed the `generated_at` timestamp from the most recent `best_bets_today.json` in the footer so users know data freshness.

## Priority 3: SEO & Discovery

### Structured Data Markup
- Add `Organization` JSON-LD schema to `index.html` to improve Google search appearance.
- Add `SoftwareApplication` schema to each project card for better indexing.

### Open Graph Tags
- Add `og:title`, `og:description`, `og:image` to each HTML page for better social sharing previews.
