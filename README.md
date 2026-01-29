<img src="data_files/logo.png" alt="Logo" width="220" />

# Betting Oracle — Data Analysis for Sports Betting

> Betting Oracle is a compact hub that collects and showcases my sports‑prediction projects and dashboards in one place. Each card below links to a repository or app and includes a short summary so you can quickly explore the model, data sources, and how to run the project. Click an icon to open the repo or follow the quick‑start steps in each README to run the Streamlit apps locally.

---

## Equine Edge - Horse Racing Predictions
### [www.equine-edge.horse](http://equine-edge.horse)

A comprehensive ML system for UK horse-racing with a Streamlit dashboard, data pipeline, and XGBoost win prediction model. Includes a race profitability scorer, fixture calendar with predicted scores, and utilities to convert probabilities into betting odds.

The system identifies the most profitable races to bet on using a smart scoring algorithm that factors in class quality, prize money, course tier, and field size. The XGBoost model predicts win probabilities with 18 carefully engineered features, and the dashboard lets you filter by year, course, and horse to explore patterns and compare model odds against bookmaker odds for value bets.

---

## Pitch Oracle - Premier League Predictor
### [www.pitch-oracle.com](http://pitch-oracle.com)

A Premier League match predictor with a Streamlit UI and ensemble modeling (XGBoost, Random Forest, Gradient Boosting, Logistic Regression) plus optional neural/LSTM support. Shows upcoming fixtures, predicted probabilities, referee/manager statistics, and model-comparison metrics with scripts to fetch and process fixtures.

This project goes deeper than just match outcomes—it analyzes referee tendencies, manager performance trends, and how recent team form impacts results. The ensemble approach combines multiple algorithms and achieves 3.5% higher accuracy than using XGBoost alone. You can explore historical data, see detailed statistics by referee or manager, and understand the confidence level behind each prediction.

---

## Gridiron Oracle - NFL Predictions
### [www.gridiron-oracle.com](http://gridiron-oracle.com)

A sophisticated NFL analytics platform with multi-model ML pipelines and a multi-page Streamlit dashboard. Offers player props, DraftKings Pick 6 tools, automated nightly prediction updates, and production-ready features for generating and exporting betting insights.

This is one of the most feature-rich systems—it can predict spreads, moneylines, and player prop performances with separate specialized models. The dashboard includes a bankroll management tool to calculate optimal bet sizes, an in-app notification system to alert you about high-confidence opportunities, and automated nightly updates that regenerate predictions using the latest game data and betting lines. There's even a per-game detail view with shareable links and historical play-by-play analysis.

---

## Gridlocked Oracle - F1 Analysis
### [www.gridlocked.racing](http://gridlocked.racing)

Formula 1 data analysis tools and a Streamlit app that generate race analytics from F1DB and FastF1 sources. Includes generators for CSV/JSON datasets, multiple model support, email notifications, and extensive feature engineering for predictive modeling.

With 86+ engineered features and support for four different ML algorithms (XGBoost, LightGBM, CatBoost, Ensemble), this system achieves a Mean Absolute Error of 1.94 for predicting race finishes. It pulls data from F1DB's massive historical dataset plus real-time race control messages from FastF1, and includes advanced filtering for over 30 different parameters. Email notifications deliver pre-race predictions with team colors and driver rankings, making it easy to stay updated on every Grand Prix.

---

## Bracket Oracle - March Madness Predictor
### [www.bracket-oracle.com](http://bracket-oracle.com)

A March Madness betting prediction system that integrates historical data, KenPom and BartTorvik efficiency ratings, and ML models. Provides real-time predictions, underdog value detection, Kelly Criterion sizing, and automated data pipelines for tournament analytics.

This system combines a decade of tournament data with advanced efficiency metrics from KenPom and BartTorvik to improve spread predictions by 8.4%. It automatically detects underdog value bets where the model disagrees with the sportsbook odds, calculates optimal bet sizing using Kelly Criterion, and continuously updates as new team data arrives. The NCAA selection is populated in real time, and the system automatically canonicalizes team names across all data sources so you get consistent, clean predictions.

---

## Shared Components

For consistent branding across all Betting Oracle applications, use the shared footer component. This provides a footer with the Betting Oracle logo and a link back to this portfolio site.

**Option 1: Copy the footer.py file to each app repository**
```python
# Copy footer.py from this repository to your app's directory
from footer import add_betting_oracle_footer

# At the end of your Streamlit app
add_betting_oracle_footer()
```

**Option 2: Copy the HTML directly into your app**
```python
import streamlit as st

# At the end of your app
footer_html = """
<div style="text-align: center; padding: 20px 0; border-top: 1px solid #e0e0e0; margin-top: 40px;">
    <p style="margin: 0 0 10px 0; font-size: 14px; color: #666; font-family: sans-serif;">
        Powered by <a href="https://www.betting-oracle.com" target="_blank" style="color: #3b82f6; text-decoration: none; font-weight: bold;">Betting Oracle</a>
    </p>
    <p style="margin: 0 0 15px 0; font-size: 12px; color: #888; font-family: sans-serif;">
        Sports Prediction Analytics
    </p>
    <a href="https://www.betting-oracle.com" target="_blank">
        <img src="https://raw.githubusercontent.com/gmalbert/betting-oracle/main/data_files/logo.png"
             alt="Betting Oracle Logo"
             style="height: 60px; width: auto; border: none;">
    </a>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)
```

---

© 2026 Betting Oracle
