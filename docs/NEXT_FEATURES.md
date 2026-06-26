# Betting Oracle Portfolio — Next 5 Features to Implement

> **Based on:** Codebase gap analysis as of July 2025

---

## Feature 1: Dark/Light Mode Toggle

**Why:** The portfolio site is entirely static HTML/CSS but has no dark mode support. Given that many Betting Oracle Streamlit apps support day/night themes, the portfolio site should match. This is a quick enhancement with high visual impact.

**How:**
1. Add a `<button id="theme-toggle">` to the header in `index.html` (and the other two pages)
2. In a minimal inline `<script>`, toggle a `class="dark"` on `<body>` and persist to `localStorage`
3. In `styles.css`, add a `body.dark` block that overrides the `:root` CSS variables (background, card colors, text, nav)
4. Apply the same button and script block to `packages.html` and `machine-learning-models.html`

**Complexity:** Low

---

## Feature 2: Live "Last Updated" Badges on Project Cards

**Why:** Each sport app writes a `data_files/best_bets_today.json` with a `meta.generated_at` timestamp. Displaying a freshness badge ("Updated 2h ago" / "Stale: 2 days") on each project card would give portfolio visitors confidence that the apps are actively maintained.

**How:**
1. Add a GitHub Actions workflow in `betting-oracle` that fetches each sport repo's `best_bets_today.json` (public GitHub raw URLs) once per day
2. Write the `generated_at` timestamps to a `data_files/app_status.json` file committed to the repo
3. Add a tiny `<script>` in `index.html` that reads `app_status.json` and injects freshness badges into each project card
4. Fallback: if `app_status.json` is missing or stale, show no badge (don't break the page)

**Complexity:** Medium

---

## Feature 3: Performance Scorecard Section

**Why:** Portfolio visitors ask "does this actually work?" A dedicated performance section (or a `performance.html` page) sourcing aggregate ROI stats from the sports-picks-grid performance leaderboard would directly answer this and build credibility.

**How:**
1. Add `performance.html` with the same header/nav/footer structure as existing pages
2. Embed a static table (updated by the same GitHub Action as Feature 2) showing each sport app's 30-day win rate and ROI
3. Pull data from `sports-picks-grid` data cache via public GitHub raw URL
4. Add "Performance" nav link to all three existing pages
5. Include a disclaimer: "Past performance does not guarantee future results"

**Complexity:** Medium

---

## Feature 4: App Health Status Indicators

**Why:** Each sport app has a GitHub Actions workflow that runs nightly. Displaying a green/yellow/red indicator on each project card based on the last workflow run status would show which apps are actively updated vs stale or broken.

**How:**
1. GitHub provides public workflow badge URLs: `https://github.com/gmalbert/{repo}/actions/workflows/{workflow}.yml/badge.svg`
2. For each project card, add a small `<img src="...badge.svg">` tag using the relevant sport repo's daily workflow badge
3. Badges are SVG files served directly by GitHub — no backend needed
4. Position the badge in the top-right corner of each card (the GitHub link icon is already positioned there)

**Complexity:** Low

---

## Feature 5: Blog / Case Study Section

**Why:** Demonstrating methodology depth (e.g., the NFL spread inversion fix, IPL toss factor discovery) builds SEO and establishes the portfolio as a serious analytics project rather than a simple link page. A `blog.html` page with 3–5 case studies would be a high-value addition.

**How:**
1. Create `blog.html` following the same HTML/CSS structure as existing pages
2. Write 3–5 case study articles (500–800 words each) in `<article>` elements:
   - "How We Found a 90% ROI Edge in NFL Spread Betting" (the spread inversion fix)
   - "Why Toss Matters: The IPL Dew Factor Analysis"
   - "Calibrating Soccer Models: Reliability Diagrams Explained"
3. Add a "Blog" nav link to all existing pages
4. No CMS needed — static HTML articles are sufficient for the portfolio context

**Complexity:** Low
