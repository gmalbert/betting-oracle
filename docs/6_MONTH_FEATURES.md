# Betting Oracle (Portfolio Site) — 6-Month Feature Roadmap

## Month 1: Content & Freshness

- **Auto-update cards** — Pull live `best_bets_today.json` from each repo via a GitHub Action and show today's pick count per sport directly on the portfolio index cards.
- **Last-updated badge** — Small "Updated 2h ago" badge on each sport card.
- **Dark mode toggle** — CSS custom properties already support theming; wire up a `prefers-color-scheme` media query and a manual toggle button.

## Month 2: Navigation Improvements

- **Sport search bar** — Add a quick-filter input above the card grid so users can type "NHL" or "golf" to jump to the relevant card.
- **Tag filtering** — Tag cards as "Season Active" / "Off-season" and allow filtering by tag.
- **Anchor deep links** — Each card gets a stable `id` so users can share direct links (e.g., `betting-oracle.com#nfl`).

## Month 3: Performance Dashboard

- **Aggregate ROI widget** — A simple inline table showing cumulative ROI from each app's `performance` endpoint, refreshed daily by GitHub Action.
- **Top pick of the day** — Highlight today's single highest-edge bet across all sports in a hero banner.

## Month 4: Community & Engagement

- **Email subscription** — Simple Mailchimp or Buttondown form to receive the daily top picks digest.
- **Share buttons** — One-click share to Twitter/X for today's best bet with auto-generated card image.
- **Discord webhook** — Post the daily top pick to a Discord channel via GitHub Action.

## Month 5: Mobile Optimisation

- **Progressive Web App (PWA)** — Add `manifest.json` and a service worker so users can install the site on their home screen.
- **Responsive card layout improvements** — Switch from CSS grid to container queries so cards scale gracefully between 320px and 1440px.
- **Touch-friendly navigation** — Hamburger menu for small screens with smooth CSS transitions.

## Month 6: Analytics & Monetisation

- **Simple analytics** — Integrate Plausible or Fathom (privacy-first) to track which sport cards get the most traffic.
- **Premium tier landing page** — Placeholder page describing a hypothetical "Pro" tier with private model details and earlier picks.
- **Affiliate link tracking** — UTM-tagged links to DraftKings/FanDuel for partner tracking.
