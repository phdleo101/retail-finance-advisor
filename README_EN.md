# Retail Finance AI Advisor

> An intelligent wealth management product recommendation and asset allocation system based on risk assessment.

[![Live Demo](https://img.shields.io/badge/Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://retail-finance-advisor-jwhilqzhrdnwwp2zzfpnue.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/phdleo101/retail-finance-advisor)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

## Overview

A retail finance AI advisor that assesses investor risk tolerance (C1-C5 five levels) through an interactive risk assessment questionnaire, matches suitable wealth management products (50-product database), and generates personalized asset allocation plans using the Standard & Poor's Four-Quadrant Model.

**Core Positioning**: Investment reference tool (not investment advice), compliant with financial suitability management regulations.

## Features

- **Risk Assessment**: 10-question interactive questionnaire -> C1-C5 scoring -> multi-dimensional visualization
- **Product Recommendation**: 50 wealth management products -> risk level matching -> multi-criteria filtering
- **Intelligent Q&A**: Dify RAG streaming Q&A -> financial knowledge base -> local fallback
- **Asset Allocation**: Standard & Poor's four-quadrant model -> investment amount allocation -> Plotly interactive visualization

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| RAG Engine | Dify Cloud (Streaming SSE) + LRU Cache (20) |
| Visualization | Plotly |
| Data | JSON + Markdown |
| Deployment | Streamlit Community Cloud |

## Quick Start

```bash
pip install -r requirements.txt
streamlit run src/streamlit_app.py
```

### Configure Dify RAG (Optional)

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in Dify API credentials. The system works without configuration by falling back to local knowledge base mode.

## Data

### Product Database (50 products)

| Risk Level | Count | Typical Products |
|---|---|---|
| R1 Low Risk | 10 | Savings, CDs, Money Market Funds |
| R2 Medium-Low | 10 | Government Bonds, Bond Funds, Bank Wealth Mgmt |
| R3 Medium Risk | 10 | Hybrid Funds, Convertible Bond Funds, REITs |
| R4 Medium-High | 10 | Stock Funds, Index Funds, QDII |
| R5 High Risk | 10 | Sector Funds, Private Equity, Structured Products |

### Standard & Poor's Four-Quadrant Model

| Quadrant | Name | Ratio | Purpose |
|---|---|---|---|
| 1 | Daily Expenses | 10% | 3-6 months living expenses |
| 2 | Protection | 20% | Insurance & emergency |
| 3 | Growth | 30% | Higher returns |
| 4 | Wealth Preservation | 40% | Retirement & education |

## Compliance Statement

- This system provides investment reference only, not investment advice or product sales
- Suitability management: C1-C5 investors can only purchase products at or below their risk level
- Complies with asset management regulations: no guaranteed returns, net-value operations
- Investment involves risk

## License

MIT
