# 📊 Amazon Sales Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)

[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

[![License](https://img.shields.io/badge/License-MIT-success)](LICENSE)

[![CI](https://github.com/arpitpatelcell/Amazon-Sales-Analytics-Dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/arpitpatelcell/Amazon-Sales-Analytics-Dashboard/actions/workflows/ci.yml)

## Project Overview

The Amazon Sales Analytics Dashboard is a data analytics application built with Python and Streamlit. It analyzes Amazon product data to generate business insights through interactive charts, filters, and KPIs — built with a modular, testable, production-style architecture.

## Objective

- Analyze Amazon sales dataset
- Perform data cleaning and preprocessing
- Generate business insights
- Build interactive visualizations
- Develop a professional analytics dashboard
* Perform data cleaning and preprocessing
* Generate business insights
* Create interactive visualizations
* Build a professional, maintainable analytics dashboard

## Tech Stack
| Category | Tools |
|---|---|
| Language | Python 3.11 |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Matplotlib, Seaborn |
| Web App Framework | Streamlit |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Notebook | Jupyter |

## Project Structure
```
Amazon-Sales-Analytics-Dashboard/
│
├── dashboard/
│   ├── app.py                  # Main entry point (UI orchestration only)
│   ├── config.py                # Centralized settings (paths, theme, cache TTL)
│   ├── data_loader.py           # Data loading, cleaning, validation
│   ├── components/
│   │   ├── styles.py            # CSS theme
│   │   ├── sidebar.py           # Navigation + filters
│   │   ├── kpi_cards.py         # KPI card rendering
│   │   └── charts.py            # All chart-building functions
│   └── utils/
│       └── logger.py            # Centralized logging
│
├── dataset/
│   └── amazon.csv               # Source dataset (not committed if large)
│
├── notebook/
│   └── Amazon_Sales_Analysis.ipynb
│
├── output/
│   ├── cleaned_data.csv
│   └── charts/
│
├── tests/
│   └── test_data_loader.py      # Automated unit tests
│
├── .github/workflows/ci.yml     # Automated testing + linting on every push
├── Dockerfile                   # Containerized deployment
├── .env.example                 # Environment variable template
├── requirements.txt             # Version-pinned dependencies
├── .gitignore
└── README.md
```

## Architecture
The app follows a simple **separation of concerns**: UI, data logic, and configuration each live in their own layer.

```
┌─────────────┐     ┌───────────────┐     ┌──────────────────┐
│  config.py   │────▶│  data_loader   │────▶│  app.py (UI)     │
│ (settings)   │     │ (clean/valid.) │     │  + components/*  │
└─────────────┘     └───────────────┘     └──────────────────┘
```
This means: changing a color needs only `components/styles.py`, adding a chart needs only `components/charts.py`, and the data-cleaning logic can be unit-tested without ever starting the Streamlit server.

## Features
* Interactive multi-page dashboard (Home / Analytics / Product Explorer)
* Sidebar filters (category, rating range, price range)
* 5 live KPI cards
* 13 interactive Plotly charts across Pricing, Ratings, Categories, and Correlation tabs
* Flexible column-name detection (works across common Amazon CSV schema variants)
* Product search, sort, and CSV export
* Centralized logging (`logs/app.log`)
* Automated tests with Pytest
* CI pipeline (lint + test on every push)
* Docker support for one-command deployment anywhere

## How to Run

### Option 1 — Local (Python)
```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

### Option 2 — Docker
```bash
docker build -t amazon-dashboard .
docker run -p 8501:8501 amazon-dashboard
```

### Configuration (optional)
Copy `.env.example` to `.env` to override defaults like the dataset path or cache duration:
```bash
cp .env.example .env
```

## Running Tests
```bash
pip install pytest
pytest tests/ -v
```

## Continuous Integration
Every push and pull request to `main` automatically runs linting (`flake8`) and the full test suite via GitHub Actions — see `.github/workflows/ci.yml`.

## Dataset
Amazon Product Sales Dataset (place your `amazon.csv` inside `dataset/`).

## Future Improvements
* Sales forecasting with time-series models
* Machine learning-based price/rating prediction
* User authentication
* Cloud deployment (Streamlit Community Cloud / Render)
* Real-time analytics with scheduled data refresh

## Author
**Arpit Patel**

B.Tech CSE Student · Data Science & AI Enthusiast
