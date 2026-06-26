# Betting Oracle Suggest Page Design Handoff

## Context

The current home page functions as a full project directory. It shows every Betting Oracle app in a single four-column card grid, which makes the page feel dense and hard to scan. The enhancement ideas in `MODEL_SUGGESTED_ENHANCEMENTS.md` are useful, but adding freshness badges, health states, and performance metadata directly onto the current grid would make the page feel even busier.

The recommended direction is to turn the home page into a curated overview and move the complete app catalog into a more structured project explorer.

## Current Issues

- Too many project cards appear at once on `index.html`.
- The grid gives every app equal weight, so visitors do not know where to start.
- Visible URLs on every tile add visual noise without adding much decision value.
- Most meaningful app descriptions are currently hidden in HTML comments.
- There is no grouping by sport type, model type, or project maturity.
- Proposed status/freshness enhancements need a cleaner layout before they are added.

## Recommended Information Architecture

```text
Header
------------------------------------------------
Featured / Active Picks
[Top 3-4 larger project cards]

Sports Categories
[Football] [Soccer] [Racing] [Court / Field] [Combat / Other]

Project Explorer Preview
[Filter chips] [Search]
[8 compact cards max]
[View all projects]

Trust / Status Strip
[Updated today] [17 apps] [Model families] [Active repos]
```

## Primary Design Direction

### 1. Make The Home Page Curated

The home page should communicate what Betting Oracle is and direct visitors to the strongest or most active apps. It should not try to show the entire ecosystem at full density.

Suggested first viewport:

- Small brand header with logo and navigation.
- Short page title or intro line.
- Featured app row with 3-4 priority projects.
- A visible hint of the next section below the fold.

### 2. Add A Dedicated Full Catalog Page

Create a new `projects.html` page for the full directory of apps. This page can carry the heavier browsing UI:

- Search input.
- Sport category filters.
- Compact project cards.
- Status/freshness badges.
- Links to app and GitHub.

This keeps `index.html` lighter while still preserving access to every project.

### 3. Group Projects By Category

Use sport-family sections instead of one undifferentiated grid.

Suggested groups:

- Major US Sports: NFL, NBA, MLB, NHL, college football, college basketball.
- Soccer: Premier League, MLS, Bundesliga, La Liga, Ligue 1, World Cup.
- Racing: Horse racing, Formula 1, golf.
- Individual / Match Sports: Tennis, darts, boxing.

These groups make the system easier to understand and give future status badges a natural place to live.

### 4. Replace Visible URLs With Clear Actions

The current card URL text repeats the destination and increases clutter. Prefer:

- Primary action: `Open App`
- Secondary icon action: GitHub icon
- Optional small metadata line: sport or league

Example card structure:

```text
Gridiron Oracle
NFL
Spread, moneyline, totals, player props
[Open App] [GitHub icon]
```

### 5. Add Metadata Chips, Not Paragraphs

The hidden descriptions contain valuable detail, but full paragraphs would make the page too heavy. Convert key facts into short chips.

Examples:

- `XGBoost`
- `Player props`
- `Daily refresh`
- `Value bets`
- `Kelly sizing`
- `Live odds`

Use no more than 3-4 chips per card.

## Visual Suggestions

### Home Page Layout

```text
+--------------------------------------------------+
| Logo                         Home Projects Models |
+--------------------------------------------------+
| Betting Oracle                                   |
| Sports prediction apps powered by model-driven   |
| odds analysis, value detection, and live data.    |
|                                                  |
| [17 apps] [Daily refreshes] [ML ensembles]        |
+--------------------------------------------------+
| Featured Apps                                    |
| [Large Card] [Large Card] [Large Card]            |
+--------------------------------------------------+
| Explore By Sport                                 |
| [Football] [Soccer] [Racing] [Combat] [Other]     |
+--------------------------------------------------+
| Project Preview                                  |
| [Compact] [Compact] [Compact] [Compact]          |
| [View all projects]                              |
+--------------------------------------------------+
```

### Featured Card

```text
+--------------------------------------+
| [Logo]  Gridiron Oracle              |
|         NFL predictions and props     |
|                                      |
|         XGBoost  Props  Daily data    |
|                                      |
|         [Open App] [GitHub]           |
+--------------------------------------+
```

### Compact Catalog Card

```text
+---------------------------+
| [Logo]                    |
| Betting Cleanup           |
| MLB                       |
| XGBoost  Live odds        |
| Updated 3h ago            |
| [Open] [GitHub]           |
+---------------------------+
```

### Status Strip

```text
+--------------------------------------------------+
| App Health: 14 fresh · 2 stale · 1 paused          |
| Latest data refresh: Today, 8:15 AM ET             |
+--------------------------------------------------+
```

## Enhancement Placement

The ideas in `MODEL_SUGGESTED_ENHANCEMENTS.md` should be placed as follows:

| Enhancement | Recommended Placement |
|---|---|
| Signal freshness indicator | Compact badge on `projects.html`; aggregate summary on home |
| Stale feed warning | Catalog card badge and optional filter |
| Cross-sport correlation warning | Future detail page or dashboard, not home |
| Consensus pick aggregation | Future performance/status page |
| Footer CTA A/B test | Footer only |
| Footer version stamp | Footer or status strip |
| Organization JSON-LD | All pages |
| SoftwareApplication schema | Project cards or `projects.html` |

## Implementation Phases

### Phase 1: Reduce Home Page Density

- Add a short intro/overview section to `index.html`.
- Convert the current project grid into a featured section plus a smaller preview.
- Remove visible URL text from cards.
- Add a `Projects` nav link.

### Phase 2: Create Full Project Catalog

- Add `projects.html`.
- Move the complete project list there.
- Add category sections or filter chips.
- Use compact cards with sport, tags, app link, and GitHub link.

### Phase 3: Add Status And Freshness

- Add `data_files/app_status.json`.
- Inject freshness badges with lightweight vanilla JavaScript.
- Show aggregate status on the home page.
- Show per-card badges on `projects.html`.

### Phase 4: Add Performance / Trust Surface

- Consider a future `performance.html` page.
- Include 30-day win rate, ROI, and disclaimer.
- Keep the home page limited to summary stats.

## File Touchpoints

| File | Expected Changes |
|---|---|
| `index.html` | New home layout, featured apps, project preview, status strip |
| `projects.html` | New full catalog page |
| `styles.css` | Shared card, chip, status, category, and responsive styles |
| `data_files/` | Existing logos reused |
| `docs/MODEL_SUGGESTED_ENHANCEMENTS.md` | Keep as feature source; do not overload home page |

## Design Guardrails

- Avoid showing all apps at equal visual weight on the home page.
- Keep card text short and scannable.
- Use chips for metadata instead of long paragraphs.
- Keep card border radius at 8px or less to match the existing site.
- Avoid adding multiple badges to every card until the layout is simplified.
- Keep the site static: HTML, CSS, and small vanilla JavaScript only.
- Ensure mobile cards stack cleanly with no horizontal scrolling.

## Suggested Definition Of Done

- Home page has a clear hierarchy and no longer feels like a full directory.
- Full project list is still available from navigation.
- Cards have clear app and GitHub actions.
- Sport grouping or filtering is available on the catalog page.
- The page can support future freshness/status badges without feeling crowded.
