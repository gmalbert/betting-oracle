> **AI Onboarding Guide** — Static site, no runtime server required.

# Betting Oracle Portfolio — Site Summary

## What This App Does

Static HTML portfolio website for the Betting Oracle suite of sports prediction apps. Three pages link to all individual sport prediction repositories (each hosted as separate Streamlit apps on Streamlit Cloud). The `footer.py` file in this repo is shared across all Streamlit sibling apps to provide a consistent "Powered by Betting Oracle" footer.

## Quick Start

Open `index.html` in any browser. No server, no build, no dependencies.

```bash
# Optional: quick local server for responsive testing
python -m http.server 8080
# Then open: http://localhost:8080
```

## Tech Stack

| Layer | Technology |
|---|---|
| Pages | Pure HTML5 (semantic markup) |
| Styling | CSS3 with custom properties, no frameworks |
| JavaScript | None (vanilla JS for copyright year only) |
| Build process | None |
| Backend | None |

## Key Files

| File | Purpose |
|---|---|
| `index.html` | Main portfolio — project cards for all Betting Oracle apps |
| `packages.html` | Common Python packages used across projects |
| `machine-learning-models.html` | ML model descriptions and use cases |
| `styles.css` | All styling — CSS variables, responsive grid, hover effects |
| `footer.py` | Shared footer for Streamlit sibling apps (`add_betting_oracle_footer()`) |
| `betting_oracle_footer.html` | Pre-rendered footer HTML (used by `footer.py`) |
| `data_files/` | Static assets: logos, icons, favicons |

## Page Structure

All three HTML pages share the same pattern:
```html
<header>
  <nav>Home | Packages | Models</nav>
</header>
<main class="grid">
  <article class="card">
    <div class="card-image"><!-- left side, icon --></div>
    <div class="card-body"><!-- right side, title, description, GitHub link --></div>
  </article>
  ...
</main>
<footer>...</footer>
```

## Adding a New Project Card

In `index.html`, add inside `.grid`:
```html
<article class="card">
  <div class="card-image">
    <img src="data_files/your-icon.png" alt="App Name icon">
  </div>
  <div class="card-body">
    <h2>
      App Name
      <a href="https://github.com/gmalbert/your-repo" target="_blank" rel="noopener noreferrer"
         class="gh-link"><img src="data_files/github-icon.png" alt="GitHub"></a>
    </h2>
    <p>Description text here.</p>
    <a href="https://your-app.streamlit.app" target="_blank" rel="noopener noreferrer">Live App</a>
  </div>
</article>
```

## Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| > 900px | Multi-column grid |
| ≤ 900px | Single column, cards stack |
| ≤ 700px | Compact spacing, smaller fonts |

## Using the Shared Footer in Streamlit Apps

```python
# In any Streamlit sibling app:
from footer import add_betting_oracle_footer
add_betting_oracle_footer()  # Call at the bottom of predictions.py after pg.run()
```

## Conventions

- External links always include `target="_blank" rel="noopener noreferrer"`
- Images go in `data_files/` — reference with relative paths
- Theme changes → update CSS custom properties in `:root` in `styles.css`
- No JavaScript frameworks — vanilla JS only (e.g., `document.getElementById('year').textContent = new Date().getFullYear()`)

## Common Gotchas

- No build step — changes are live immediately after save
- If the footer looks broken in a sibling app, check `betting_oracle_footer.html` for unclosed tags
- Images must have `alt` attributes for accessibility
