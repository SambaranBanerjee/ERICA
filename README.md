# ERICA: E-Commerce Revenue & Customer Intelligence Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)](https://www.postgresql.org/)
[![Power BI](https://img.shields.io/badge/Dashboard-Power%20BI-yellow)](https://powerbi.microsoft.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange)](https://scikit-learn.org/)

An end-to-end Data Analytics and Engineering portfolio project that processes **100k+ marketplace orders** to unlock revenue performance, logistics optimizations, customer lifetime value cohorts, and predictive churn/satisfaction mitigation patterns.

---

## 📌 Business Problem & Objectives

An enterprise e-commerce marketplace demands deeper visibility into operational friction points and customer lifecycle values to sustain growth. This platform was built to engineer data pipelines and construct analytical assets that answer critical business questions:

1. **Revenue Drivers:** Which product categories, geographic states, and commercial sellers dominate market share?
2. **Logistics Bottlenecks:** What is the precise economic threshold where shipping delays trigger negative customer reviews?
3. **Customer Value Cohorts:** Who are our champions, loyalists, at-risk users, and completely lapsed customers?
4. **Predictive Mitigation:** Can we identify high-risk orders *before* they receive a poor evaluation score?
5. **Operational Key Indicators:** What data vectors should executive leadership track weekly to safeguard marketplace health?

---

## 🛠️ Tech Stack & Architecture

| Lifecycle Layer | Tools & Technologies |
| :--- | :--- |
| **Data Orchestration & Cleaning** | Python, Pandas, NumPy, Pathlib |
| **Cloud Storage & Relational Warehousing**| Cloud PostgreSQL, Prisma Postgres, Connection Pooling |
| **Advanced Querying & Analytics** | PostgreSQL SQL, Common Table Expressions (CTEs), Window Functions |
| **Business Intelligence Visualizations** | Power BI Desktop, Star Schema Data Modeling, DAX Measures |
| **Predictive Machine Learning Engineering**| Scikit-Learn, Composite ML Pipelines, Hyperparameter Classifiers |
| **Project Tracking & Reproducibility** | Python Virtual Environments, Git, Dotenv Architecture |

### Pipeline Dataflow Architecture

```text
  [ Raw Olist CSV Data ] 
            ↓
  [ Python Data Cleaning Engine ] 
            ↓
  [ Processed CSV Artifacts ] 
            ↓ (SQLAlchemy Engine Integration)
  [ Cloud PostgreSQL Warehouse Schema ]
            ↓
  [ Relational Analytical Views (Fact & Dim) ] ────→ [ Power BI Dashboards ]
            ↓                                     ───→ [ DAX Metrics Layer ]
  [ Advanced SQL Analytical Engines ]
            ↓
  [ Recency, Frequency, Monetary (RFM) Segmentation Engine ]
            ↓
  [ Scikit-Learn Binary Classification Pipeline ]
            ↓
  [ Markdown Executive Summary & Data Insight Reports ]
```
### Project Repository Structure
ecommerce-revenue-intelligence-analytics/
│
├── README.md                           # Main portfolio showcase documentation
├── requirements.txt                    # Project package dependencies
├── .gitignore                          # Protected file exclusions (inc. .env files)
│
├── data/                               # Local staging storage
│   ├── raw/                            # Immutable source files
│   └── processed/                      # Output from clean data engines
│
├── database/                           # Warehousing configurations
│   ├── 01_create_indexes.sql          # Query performance tuning indexes
│   ├── 02_create_analytics_views.sql   # Relational Base Fact/Dimension structures
│   ├── 03_create_powerbi_views.sql     # Pre-aggregated Power BI reporting tables
│   └── 04_create_rfm_views.sql         # SQL Recency, Frequency, Monetary calculations
│
├── src/                                # Production Engine Source Code
│   ├── load_data.py                    # Schema and environment file integrity verification
│   ├── clean_data.py                   # High-performance pipeline feature engineering
│   ├── create_postgres_warehouse.py    # Cloud database loader and view executor
│   ├── run_postgres_sql_analysis.py    # SQL business logic query runner
│   ├── generate_business_insights.py   # Automated markdown data analysis report
│   ├── create_rfm_segments.py          # Customer value cohort engine
│   ├── train_low_review_model.py       # Scikit-learn feature modeling pipeline
│   └── generate_final_project_summary.py # Final document compilation script
│
├── reports/                            # Compiled Project Artifacts
│   ├── sql_outputs/                    # Comma-separated relational results
│   ├── rfm_outputs/                    # Customer cohort groupings data
│   ├── model_outputs/                  # ML Evaluation parameters & JSON properties
│   ├── business_insights_report.md     # Detailed Day 7 Analytics insights
│   ├── rfm_segmentation_report.md      # Detailed Day 8 Segmentation insights
│   ├── low_review_prediction_report.md # Detailed Day 9 Machine Learning insights
│   └── final_executive_summary.md      # Executive-ready project status brief
│
├── dashboards/                         # Visual Intelligence Resources
│   ├── powerbi/                        # .pbix reporting files
│   └── screenshots/                    # Dashboard page image files
│
└── docs/                               # Phase-specific design files
    ├── problem_statement.md            
    ├── data_dictionary.md              
    └── final_project_summary.md

### Execution Guide

## 1. Environment Initialization
# Generate the isolated virtual environment
python -m venv .venv

# Activate the local virtual environment (Windows PowerShell)
.\.venv\Scripts\activate

# Install system packages and requirements
pip install -r requirements.txt

## 2. Environment Variables Configuration
DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DB_NAME?sslmode=require"
POSTGRES_SCHEMA="olist"

## 3. Step-by-Step Data Pipeline Execution
# Step 1: Verify data integrity requirements
python src/load_data.py

# Step 2: Run cleaning transformations and extract features
python src/clean_data.py

# Step 3: Initialize warehouse schemas and load data to PostgreSQL
python src/create_postgres_warehouse.py

# Step 4: Run advanced query validations
python src/run_postgres_sql_analysis.py

# Step 5: Export reporting summaries
python src/generate_business_insights.py

# Step 6: Construct the customer RFM matrices
python src/create_rfm_segments.py

# Step 7: Train the predictive model pipelines
python src/train_low_review_model.py

# Step 8: Build the project summary logs
python src/generate_final_project_summary.py
