"""
Day 8: RFM Customer Segmentation

This script:
1. Reads RFM segment data from PostgreSQL
2. Exports customer-level RFM data
3. Exports segment-level summary
4. Creates a markdown explanation report

Run:
    python src/create_rfm_segments.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

from config import BASE_DIR


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "olist")

REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_DIR = REPORTS_DIR / "rfm_outputs"

CUSTOMER_RFM_FILE = OUTPUT_DIR / "customer_rfm_segments.csv"
SEGMENT_SUMMARY_FILE = OUTPUT_DIR / "rfm_segment_summary.csv"
RFM_REPORT_FILE = REPORTS_DIR / "rfm_segmentation_report.md"


def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def get_engine():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing. Add it to your .env file.")

    # Fix the deprecated postgres:// prefix dynamically
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return create_engine(url, pool_pre_ping=True)


def export_rfm_segments() -> None:
    print_section("Day 8: RFM Customer Segmentation")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    engine = get_engine()

    customer_rfm = pd.read_sql_query(
        f"""
        SELECT *
        FROM {POSTGRES_SCHEMA}.pbi_rfm_segments
        ORDER BY monetary DESC;
        """,
        engine,
    )

    segment_summary = pd.read_sql_query(
        f"""
        SELECT
            customer_segment,
            COUNT(*) AS customer_count,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_percentage,
            ROUND(SUM(monetary)::NUMERIC, 2) AS total_revenue,
            ROUND(AVG(monetary)::NUMERIC, 2) AS avg_monetary_value,
            ROUND(AVG(frequency)::NUMERIC, 2) AS avg_frequency,
            ROUND(AVG(recency_days)::NUMERIC, 2) AS avg_recency_days
        FROM {POSTGRES_SCHEMA}.pbi_rfm_segments
        GROUP BY customer_segment
        ORDER BY total_revenue DESC;
        """,
        engine,
    )

    customer_rfm.to_csv(CUSTOMER_RFM_FILE, index=False)
    segment_summary.to_csv(SEGMENT_SUMMARY_FILE, index=False)

    print(f"Saved customer RFM file: {CUSTOMER_RFM_FILE}")
    print(f"Saved segment summary file: {SEGMENT_SUMMARY_FILE}")

    top_segment_by_revenue = segment_summary.sort_values(
        "total_revenue", ascending=False
    ).iloc[0]

    largest_segment = segment_summary.sort_values(
        "customer_count", ascending=False
    ).iloc[0]

    report = f"""# RFM Customer Segmentation Report

## Objective

The goal of RFM analysis is to segment customers based on:

- Recency: how recently the customer purchased
- Frequency: how often the customer purchased
- Monetary: how much revenue the customer generated

---

# Methodology

Each customer was scored from 1 to 5 on:

```text
Recency Score
Frequency Score
Monetary Score```
"""
    
    RFM_REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"Saved report: {RFM_REPORT_FILE}")
    print_section("Day 8 Completed")

if __name__ == "__main__":
    export_rfm_segments()