# Betting Oracle Portfolio — Architecture

## Overview
Static HTML portfolio website showcasing all sports betting prediction projects in the Betting Oracle suite. No backend, no build process — pure HTML/CSS with a shared `footer.py` for Streamlit apps.

## Structure
```
betting-oracle/
├── index.html                  # Main portfolio (project cards)
├── packages.html               # Common Python packages
├── machine-learning-models.html # ML model descriptions
├── styles.css                  # All styling (CSS variables, responsive)
├── data_files/                 # Static assets (logos, favicons, icons)
├── footer.py                   # Shared Streamlit footer for all suite apps
└── betting_oracle_footer.html  # Raw HTML footer template
```

## Card Layout Pattern
Each project uses `<article class="card">` with:
- Left: icon/image area
- Right: title, description, GitHub link (opens `target="_blank" rel="noopener noreferrer"`)
- GitHub icon link positioned absolutely in card header

## Shared Footer (`footer.py`)
All Streamlit apps in the suite import `add_betting_oracle_footer()` from a copy of `footer.py`. The footer renders "Powered by Betting Oracle" with logo and link back to this portfolio.

## Responsive Design
- Mobile-first CSS
- Breakpoints at 900px and 700px
- CSS custom properties (`:root`) for theme colours

## No ML / No Backend
This repo is display-only. All ML logic lives in the individual sport repos. No Python dependencies required for the website itself (venv present but unused for site development).

## Development
Edit HTML/CSS directly — no compilation. Test responsiveness by resizing the browser window.
