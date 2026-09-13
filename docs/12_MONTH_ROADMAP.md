# Betting Oracle (Portfolio Site) — 12-Month Feature Roadmap

> Generated: 2026-07-31 | Horizon: August 2026 – July 2027

---

## Q1 (Aug–Oct 2026) — Portfolio Enhancement

### Feature 1 — Live Performance Dashboard

Add a "Live Results" section to the homepage showing today's picks
from all 20+ apps with real-time settlement status.

```html
<!-- index.html — add live results section -->
<section id="live-results" class="live-results-grid">
  <h2>📊 Today's Active Picks</h2>
  <div class="picks-feed" id="live-picks-container">
    <!-- Populated by fetch_live_picks.js -->
    <p class="loading">Loading today's picks...</p>
  </div>
</section>
```

```javascript
// assets/js/fetch_live_picks.js
async function loadTodayPicks() {
  const SPORTS_PICKS_API = 'https://raw.githubusercontent.com/gmalbert/sports-picks-grid/main/data_cache';
  const sports = ['MLB', 'NFL', 'NBA', 'NHL', 'EPL', 'Golf', 'Tennis'];
  const container = document.getElementById('live-picks-container');
  container.innerHTML = '';

  for (const sport of sports) {
    try {
      const resp = await fetch(`${SPORTS_PICKS_API}/${sport.toLowerCase()}.json`);
      const data = await resp.json();
      const elite = (data.bets || []).filter(b => b.tier === 'Elite').slice(0, 2);
      elite.forEach(pick => {
        const card = document.createElement('div');
        card.className = 'pick-card tier-elite';
        card.innerHTML = `
          <span class="sport-badge">${sport}</span>
          <strong>${pick.pick}</strong>
          <span class="edge">+${(pick.edge * 100).toFixed(1)}%</span>
        `;
        container.appendChild(card);
      });
    } catch (e) {
      console.warn(`Failed to load ${sport} picks:`, e);
    }
  }
}
loadTodayPicks();
setInterval(loadTodayPicks, 1800000); // refresh every 30 min
```

### Feature 2 — Model Performance Trophy Case

Add a "Track Record" section showing aggregate performance stats
across all Betting Oracle apps: win rate, ROI, total picks.

```html
<!-- Add to index.html -->
<section class="trophy-case">
  <h2>🏆 Track Record</h2>
  <div class="stats-grid">
    <div class="stat-card">
      <span class="stat-number" id="total-picks">---</span>
      <span class="stat-label">Total Picks (Season)</span>
    </div>
    <div class="stat-card">
      <span class="stat-number" id="win-rate">---%</span>
      <span class="stat-label">Win Rate</span>
    </div>
    <div class="stat-card">
      <span class="stat-number" id="roi">+---%</span>
      <span class="stat-label">ROI</span>
    </div>
    <div class="stat-card">
      <span class="stat-number" id="elite-accuracy">---%</span>
      <span class="stat-label">Elite Tier Accuracy</span>
    </div>
  </div>
</section>
```

### Feature 3 — Blog/Newsletter Section

Add a blog section with weekly betting insights. Markdown-rendered
articles about model methodology, picks recap, and market analysis.

```html
<!-- blog.html (new page) -->
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Betting Oracle — Insights Blog</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="site-header">
    <nav><!-- same nav --></nav>
  </header>
  <main class="blog-grid">
    <article class="blog-post">
      <h2>Why Our MLB Model Beat the Market by 8% This Week</h2>
      <time>July 28, 2026</time>
      <p>Our Underdog Moneyline model...</p>
    </article>
  </main>
</body>
</html>
```

### Feature 4 — Dark Mode Toggle

Implement system-preference dark mode with manual toggle.
Use CSS custom properties for seamless theme switching.

```css
/* styles.css — add dark mode */
:root {
  color-scheme: light dark;
  --bg-primary: #ffffff;
  --text-primary: #1a1a2e;
  --card-bg: #f8f9fa;
  --accent: #2196F3;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #0d1117;
    --text-primary: #e6edf3;
    --card-bg: #161b22;
    --accent: #58a6ff;
  }
}

[data-theme="dark"] {
  --bg-primary: #0d1117;
  --text-primary: #e6edf3;
  --card-bg: #161b22;
  --accent: #58a6ff;
}
```

```javascript
// assets/js/theme.js
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

// Apply saved theme on load
document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
});
```

### Feature 5 — Sport-Specific Deep Link Cards

Each sport card on index.html should deep-link to a specific tab or
section within the Streamlit app (via URL hash or query params).

```html
<!-- Update sport cards to include deep links -->
<article class="card" id="mlb-card">
  <div class="card-header">
    <img src="data_files/baseball.png" alt="Baseball" class="card-icon">
    <h3>MLB Betting Cleanup</h3>
    <a href="https://github.com/gmalbert/baseball-predictions" 
       target="_blank" rel="noopener noreferrer" class="github-icon-link">
      <!-- GitHub icon SVG -->
    </a>
  </div>
  <div class="card-body">
    <p>Three XGBoost models targeting Moneyline, Run Line, and Totals.</p>
    <div class="quick-links">
      <a href="https://baseball-predictions.streamlit.app/?page=Today" 
         target="_blank" class="deep-link-btn">Today's Picks</a>
      <a href="https://baseball-predictions.streamlit.app/?page=Performance"
         target="_blank" class="deep-link-btn">Model Performance</a>
    </div>
  </div>
</article>
```

---

## Q2 (Nov 2026 – Jan 2027) — Community & Engagement

### Feature 6 — Email Newsletter Signup

Add newsletter signup form. Weekly email digest of top picks across
all sports. Stored in a simple serverless function (Cloudflare Workers).

```html
<!-- Add to index.html -->
<section class="newsletter-signup">
  <h2>📧 Get Weekly Picks</h2>
  <p>Free weekly newsletter with top model picks across all 20+ sports.</p>
  <form id="newsletter-form" action="https://betting-oracle.workers.dev/subscribe" method="POST">
    <input type="email" name="email" placeholder="your@email.com" required>
    <button type="submit">Subscribe Free</button>
  </form>
  <p class="disclaimer">No spam. Unsubscribe anytime.</p>
</section>
```

### Feature 7 — Sports Picks Badge Widget

Provide an embeddable HTML/JS widget that other sites can include to
show today's top pick. Generated from sports-picks-grid data.

```javascript
// widget/betting-oracle-widget.js
(function() {
  const WIDGET_URL = 'https://betting-oracle.pages.dev/widget-data.json';
  const container = document.getElementById('betting-oracle-widget');
  if (!container) return;

  fetch(WIDGET_URL)
    .then(r => r.json())
    .then(data => {
      const pick = data.top_pick;
      container.innerHTML = `
        <div style="font-family:sans-serif;padding:12px;border:1px solid #ddd;border-radius:8px;max-width:300px">
          <a href="https://bettingoracle.com" style="text-decoration:none">
            <strong>🎯 Betting Oracle Top Pick</strong>
          </a>
          <p style="margin:8px 0"><b>${pick.sport}: ${pick.pick}</b></p>
          <small>Edge: ${(pick.edge*100).toFixed(1)}% | Tier: ${pick.tier}</small>
        </div>`;
    })
    .catch(() => { container.innerHTML = '<!-- Widget temporarily unavailable -->'; });
})();
```

### Feature 8 — Testimonial / Community Results Section

Add a rotating testimonials section showing community members' wins
based on model picks (user-submitted, anonymous).

### Feature 9 — FAQ & Methodology Page

Add a detailed FAQ page explaining: how models are built, what "edge"
means, how to read confidence tiers, and responsible gambling guidance.

```html
<!-- faq.html (new page) -->
<section class="faq-section">
  <h2>Frequently Asked Questions</h2>
  <details>
    <summary>What is "Edge %"?</summary>
    <p>Edge represents the difference between our model's implied probability
    and the bookmaker's implied probability. A +5% edge means our model thinks
    the outcome is 5 percentage points more likely than the market suggests.</p>
  </details>
  <details>
    <summary>What does "Tier" mean?</summary>
    <p>Tiers reflect our confidence level:<br>
    🔥 <strong>Elite</strong>: Edge > 6%, strong model agreement<br>
    ✅ <strong>Strong</strong>: Edge 3-6%<br>
    ➡ <strong>Good</strong>: Edge 1-3%<br>
    ⚪ <strong>Standard</strong>: Below 1% edge</p>
  </details>
  <details>
    <summary>Is this gambling advice?</summary>
    <p>No. Betting Oracle provides data analysis and model outputs for
    entertainment purposes only. Always gamble responsibly within your means.
    If you have a gambling problem, contact 1-800-522-4700 (NCPG).</p>
  </details>
</section>
```

### Feature 10 — Responsible Gambling Notice

Add a prominent responsible gambling notice and links to resources
on every page footer.

---

## Q3 (Feb–Apr 2027) — Visual Design Upgrade

### Feature 11 — Animated Hero Section

Replace static hero with an animated section showing live stats
(total picks today, sports active, top model) with CSS animations.

### Feature 12 — Sport Filter Bar

Add horizontal filter bar on index.html to filter project cards by
sport category: Team Sports, Individual Sports, Combat Sports, Other.

```javascript
// assets/js/filter.js
function filterCards(category) {
  const cards = document.querySelectorAll('.card');
  cards.forEach(card => {
    const cardCategory = card.dataset.category;
    card.style.display = (category === 'all' || cardCategory === category) ? '' : 'none';
  });
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === category);
  });
}
```

### Feature 13 — New App: Tennis Predictions Card

Add card for tennis-predictions app with serve stats, tour schedule
integration, and head-to-head matchup features highlighted.

### Feature 14 — Performance Charts Embedded

For each sport card, embed a tiny sparkline chart showing recent
model win rate trend (last 30 days). SVG-based, no external deps.

```javascript
// assets/js/sparklines.js
function renderSparkline(containerId, data, color = '#2196F3') {
  const svg = document.getElementById(containerId);
  const W = svg.clientWidth || 80, H = svg.clientHeight || 30;
  const min = Math.min(...data), max = Math.max(...data);
  const scale = v => H - ((v - min) / (max - min + 0.001)) * H;
  const xs = data.map((_, i) => (i / (data.length - 1)) * W);
  const pts = data.map((v, i) => `${xs[i]},${scale(v)}`).join(' ');
  svg.innerHTML = `<polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2"/>`;
}
```

### Feature 15 — App Launch Announcement System

When a new sport app launches, display a "NEW" badge on the card
and a homepage announcement banner for 2 weeks.

---

## Q4 (May–Jul 2027) — Technical Infrastructure

### Feature 16 — Cloudflare Pages Deployment with CDN

Migrate from GitHub Pages to Cloudflare Pages for better performance,
custom domain, and free CDN. Add cache headers for static assets.

### Feature 17 — Sitemap & SEO Optimization

Generate XML sitemap, add Open Graph tags for social sharing, and
optimize meta descriptions for each page.

```html
<!-- Add to all pages -->
<meta property="og:title" content="Betting Oracle — ML Sports Betting Analytics">
<meta property="og:description" content="20+ sport-specific ML models. Free predictions and edge analysis.">
<meta property="og:image" content="https://bettingoracle.com/data_files/og-image.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```

### Feature 18 — Analytics Integration

Add Plausible Analytics (privacy-friendly) to track page views, popular
sports, and conversion on newsletter signup.

```html
<!-- Add to all pages -->
<script defer data-domain="bettingoracle.com" src="https://plausible.io/js/script.js"></script>
```

### Feature 19 — App Directory JSON Feed

Publish a machine-readable JSON directory of all Betting Oracle apps
with metadata: app URL, sport, model type, last updated.

```json
// app-directory.json
{
  "apps": [
    {
      "id": "baseball-predictions",
      "name": "MLB Betting Cleanup",
      "sport": "MLB",
      "url": "https://baseball-predictions.streamlit.app",
      "github": "https://github.com/gmalbert/baseball-predictions",
      "models": ["XGBoost Moneyline", "XGBoost Run Line", "XGBoost Totals"],
      "active": true
    }
  ]
}
```

### Feature 20 — A/B Testing Framework

Simple JavaScript A/B test framework for landing page copy and CTA
button variants. Track conversion via Plausible events.

### Feature 21 — Automated Monthly Performance Report Page

Auto-generated monthly performance report page showing all apps'
win rates, ROI, and model accuracy. Published by GitHub Actions.

### Feature 22 — Contact / Collaboration Form

Add a contact form for partnerships, data contributors, or feature
requests. Route submissions to email via Cloudflare Workers.

```html
<!-- contact.html -->
<section class="contact-section">
  <h2>Get in Touch</h2>
  <form action="https://betting-oracle.workers.dev/contact" method="POST">
    <input type="text" name="name" placeholder="Your Name" required>
    <input type="email" name="email" placeholder="Your Email" required>
    <select name="subject">
      <option value="partnership">Partnership Inquiry</option>
      <option value="data">Data Contribution</option>
      <option value="feedback">App Feedback</option>
      <option value="other">Other</option>
    </select>
    <textarea name="message" rows="5" placeholder="Your message..." required></textarea>
    <button type="submit">Send Message</button>
  </form>
</section>
```

---

## Timeline Summary

| Quarter | Focus | Key Deliverables |
|---------|-------|-----------------|
| Q1 Aug–Oct 2026 | Portfolio enhancement | Live picks feed, trophy case, blog, dark mode, deep link cards |
| Q2 Nov 2026–Jan 2027 | Community | Email newsletter, embeddable widget, testimonials, FAQ page, responsible gambling notice |
| Q3 Feb–Apr 2027 | Visual design | Animated hero, sport filter bar, tennis card, sparklines, announcement system |
| Q4 May–Jul 2027 | Infrastructure | Cloudflare Pages, SEO/OG tags, analytics, app directory JSON, A/B testing, monthly report, contact form |
