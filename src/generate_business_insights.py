"""
Day 7: Generate Business Insight Report

This script:
1. Connects to online PostgreSQL using DATABASE_URL
2. Reads Power BI / analytics views
3. Extracts key business insights
4. Generates a markdown business report

Run:
    python src/generate_business_insights.py
"""

import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

from config import BASE_DIR


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "olist")

REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_FILE = REPORTS_DIR / "business_insights_report.md"


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

def read_query(engine, query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, engine)


def money(value) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.2f}"


def pct(value) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}%"


def generate_report() -> None:
    print_section("Day 7: Generating Business Insight Report")

    engine = get_engine()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    executive = read_query(
        engine,
        f"""
        SELECT *
        FROM {POSTGRES_SCHEMA}.pbi_executive_kpis;
        """,
    )

    monthly = read_query(
        engine,
        f"""
        SELECT *
        FROM {POSTGRES_SCHEMA}.pbi_monthly_revenue
        ORDER BY month_start_date;
        """,
    )

    categories = read_query(
        engine,
        f"""
        SELECT *
        FROM {POSTGRES_SCHEMA}.pbi_category_performance
        ORDER BY total_revenue DESC
        LIMIT 10;
        """,
    )

    states = read_query(
        engine,
        f"""
        SELECT *
        FROM {POSTGRES_SCHEMA}.pbi_state_performance
        ORDER BY total_revenue DESC
        LIMIT 10;
        """,
    )

    delivery = read_query(
        engine,
        f"""
        SELECT *
        FROM {POSTGRES_SCHEMA}.pbi_delivery_performance
        ORDER BY late_delivery_percentage DESC
        LIMIT 10;
        """,
    )

    delay_reviews = read_query(
        engine,
        f"""
        SELECT *
        FROM {POSTGRES_SCHEMA}.pbi_review_delay_impact;
        """,
    )

    low_review_categories = read_query(
        engine,
        f"""
        SELECT
            foi.product_category_name_english,
            COUNT(DISTINCT foi.order_id) AS reviewed_orders,
            ROUND(AVG(fr.review_score)::NUMERIC, 2) AS average_review_score,
            ROUND(
                (100.0 * SUM(fr.is_low_review) / NULLIF(COUNT(fr.review_id), 0))::NUMERIC,
                2
            ) AS low_review_percentage,
            ROUND(SUM(foi.price)::NUMERIC, 2) AS total_revenue
        FROM {POSTGRES_SCHEMA}.fact_order_items foi
        LEFT JOIN {POSTGRES_SCHEMA}.fact_reviews fr
            ON foi.order_id = fr.order_id
        WHERE foi.order_status = 'delivered'
        GROUP BY foi.product_category_name_english
        HAVING COUNT(DISTINCT foi.order_id) >= 100
        ORDER BY low_review_percentage DESC
        LIMIT 10;
        """,
    )

    e = executive.iloc[0]

    best_month = monthly.sort_values("total_revenue", ascending=False).iloc[0]
    worst_month = monthly.sort_values("total_revenue", ascending=True).iloc[0]

    top_category = categories.iloc[0]
    top_state = states.iloc[0]
    highest_late_state = delivery.iloc[0]

    best_delay_bucket = delay_reviews.sort_values(
        "average_review_score", ascending=False
    ).iloc[0]

    worst_delay_bucket = delay_reviews.sort_values(
        "average_review_score", ascending=True
    ).iloc[0]

    worst_review_category = low_review_categories.iloc[0]

    report = f"""# Business Insights Report

## Project

E-Commerce Revenue & Customer Intelligence Analytics Platform

## Data Source

Cloud-hosted PostgreSQL warehouse created from the Olist e-commerce dataset.

---

# 1. Executive Summary

The marketplace processed **{int(e['total_orders']):,} delivered orders** with total product revenue of **{money(e['total_revenue'])}** and GMV of **{money(e['gmv'])}**.

The average order value was **{money(e['average_order_value'])}**.

Customer satisfaction performance:

- Average review score: **{e['average_review_score']}**
- Low review percentage: **{pct(e['low_review_percentage'])}**
- On-time delivery percentage: **{pct(e['on_time_delivery_percentage'])}**
- Late delivery percentage: **{pct(e['late_delivery_percentage'])}**

---

# 2. Revenue Insights

## Best Revenue Month

The highest revenue month was **{best_month['purchase_year_month']}** with revenue of **{money(best_month['total_revenue'])}**.

## Lowest Revenue Month

The lowest revenue month was **{worst_month['purchase_year_month']}** with revenue of **{money(worst_month['total_revenue'])}**.

## Top Product Category

The highest revenue category was **{top_category['product_category_name_english']}**, generating **{money(top_category['total_revenue'])}** from **{int(top_category['total_orders']):,} orders**.

## Top Customer State

The highest revenue customer state was **{top_state['customer_state']}**, generating **{money(top_state['total_revenue'])}**.

---

# 3. Delivery Performance Insights

The state with the highest late delivery percentage was **{highest_late_state['customer_state']}**, with a late delivery rate of **{pct(highest_late_state['late_delivery_percentage'])}**.

This state should be investigated for logistics bottlenecks, seller distribution issues, or last-mile delivery problems.

---

# 4. Review and Satisfaction Insights

The delay bucket with the best review score was **{best_delay_bucket['delay_bucket']}**, with an average review score of **{best_delay_bucket['average_review_score']}**.

The delay bucket with the worst review score was **{worst_delay_bucket['delay_bucket']}**, with an average review score of **{worst_delay_bucket['average_review_score']}**.

This confirms that delivery performance is connected to customer satisfaction.

The product category with the highest low-review percentage was **{worst_review_category['product_category_name_english']}**, with a low-review rate of **{pct(worst_review_category['low_review_percentage'])}**.

---

# 5. Business Recommendations

## Recommendation 1: Improve delivery performance in high-delay states

Observation:
Some customer states show significantly higher late-delivery percentages.

Business Impact:
Late deliveries reduce customer satisfaction and increase the probability of low review scores.

Action:
Prioritize logistics review for states with the highest late-delivery percentage.

Expected Outcome:
Improved review scores and better customer retention.

---

## Recommendation 2: Focus marketing on high-revenue categories

Observation:
A small number of product categories contribute a large share of revenue.

Business Impact:
Prioritizing high-performing categories can improve marketing ROI.

Action:
Run category-specific campaigns for the top revenue categories.

Expected Outcome:
Higher conversion rate and improved monthly revenue.

---

## Recommendation 3: Investigate low-review product categories

Observation:
Some categories have higher low-review percentages even with meaningful order volume.

Business Impact:
Poor ratings can reduce future conversions and customer trust.

Action:
Analyze seller quality, product descriptions, delivery time, and return issues for these categories.

Expected Outcome:
Lower complaint rate and improved customer satisfaction.

---

## Recommendation 4: Track KPIs weekly

Leadership should monitor:

- Total Revenue
- Total Orders
- Average Order Value
- On-Time Delivery %
- Late Delivery %
- Average Review Score
- Low Review %
- Revenue by Category
- Revenue by State

---

# 6. Dashboard Pages Created

- Executive Summary
- Revenue Analysis
- Delivery Performance
- Review Analysis
- Customer RFM Analysis

---

# 7. Resume Impact

This project demonstrates:

- Python data cleaning
- PostgreSQL cloud warehouse loading
- SQL analytics
- Power BI dashboarding
- KPI design
- Customer segmentation
- Business recommendation writing
"""

    OUTPUT_FILE.write_text(report, encoding="utf-8")

    print(f"Report generated: {OUTPUT_FILE}")
    print_section("Day 7 Completed")


if __name__ == "__main__":
    generate_report()