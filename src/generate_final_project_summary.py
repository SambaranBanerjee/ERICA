"""
Day 10: Final Project Summary Generator

This script:
1. Reads key output files generated during the project
2. Creates a final executive summary
3. Creates final resume bullets
4. Creates GitHub checklist

Run:
    python src/generate_final_project_summary.py
"""

from pathlib import Path
import json
import pandas as pd

from config import BASE_DIR


REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"

SQL_OUTPUTS_DIR = REPORTS_DIR / "sql_outputs"
RFM_OUTPUTS_DIR = REPORTS_DIR / "rfm_outputs"
MODEL_OUTPUTS_DIR = REPORTS_DIR / "model_outputs"

FINAL_EXECUTIVE_SUMMARY = REPORTS_DIR / "final_executive_summary.md"
FINAL_PROJECT_SUMMARY = DOCS_DIR / "final_project_summary.md"
FINAL_RESUME_BULLETS = DOCS_DIR / "final_resume_bullets.md"
GITHUB_CHECKLIST = DOCS_DIR / "github_upload_checklist.md"


def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def read_json_if_exists(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def fmt_money(value):
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "N/A"


def fmt_pct(value):
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "N/A"


def generate_final_outputs():
    print_section("Day 10: Generating Final Project Summary")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    executive_kpis = read_csv_if_exists(SQL_OUTPUTS_DIR / "executive_kpis.csv")
    monthly_revenue = read_csv_if_exists(SQL_OUTPUTS_DIR / "monthly_revenue.csv")
    top_categories = read_csv_if_exists(SQL_OUTPUTS_DIR / "top_product_categories.csv")
    state_revenue = read_csv_if_exists(SQL_OUTPUTS_DIR / "revenue_by_customer_state.csv")
    rfm_summary = read_csv_if_exists(RFM_OUTPUTS_DIR / "rfm_segment_summary.csv")
    model_metrics = read_json_if_exists(MODEL_OUTPUTS_DIR / "low_review_model_metrics.json")

    total_orders = "N/A"
    total_revenue = "N/A"
    gmv = "N/A"
    average_order_value = "N/A"
    average_review_score = "N/A"
    late_delivery_percentage = "N/A"
    low_review_percentage = "N/A"

    if not executive_kpis.empty:
        e = executive_kpis.iloc[0]
        total_orders = f"{int(e.get('total_orders', 0)):,}"
        total_revenue = fmt_money(e.get("total_revenue"))
        gmv = fmt_money(e.get("gmv"))
        average_order_value = fmt_money(e.get("average_order_value"))
        average_review_score = str(round(float(e.get("average_review_score", 0)), 2))
        late_delivery_percentage = fmt_pct(e.get("late_delivery_percentage"))
        low_review_percentage = fmt_pct(e.get("low_review_percentage"))

    best_month_text = "N/A"
    if not monthly_revenue.empty:
        best_month = monthly_revenue.sort_values("total_revenue", ascending=False).iloc[0]
        best_month_text = f"{best_month.get('purchase_year_month')} with revenue {fmt_money(best_month.get('total_revenue'))}"

    top_category_text = "N/A"
    if not top_categories.empty:
        top_category = top_categories.sort_values("total_revenue", ascending=False).iloc[0]
        top_category_text = f"{top_category.get('product_category_name_english')} with revenue {fmt_money(top_category.get('total_revenue'))}"

    top_state_text = "N/A"
    if not state_revenue.empty:
        top_state = state_revenue.sort_values("total_revenue", ascending=False).iloc[0]
        top_state_text = f"{top_state.get('customer_state')} with revenue {fmt_money(top_state.get('total_revenue'))}"

    top_rfm_segment_text = "N/A"
    if not rfm_summary.empty:
        top_segment = rfm_summary.sort_values("total_revenue", ascending=False).iloc[0]
        top_rfm_segment_text = f"{top_segment.get('customer_segment')} with revenue {fmt_money(top_segment.get('total_revenue'))}"

    best_model_text = "N/A"
    best_auc = "N/A"
    if model_metrics:
        best_model = max(model_metrics, key=lambda name: model_metrics[name].get("roc_auc", 0))
        best_model_text = best_model
        best_auc = fmt_pct(model_metrics[best_model].get("roc_auc", 0) * 100)

    final_executive_summary = f"""# Final Executive Summary

## Project Title
E-Commerce Revenue & Customer Intelligence Analytics Platform

## Project Objective
The objective of this project was to build an end-to-end analytics solution for an e-commerce marketplace using Python, PostgreSQL, SQL, Power BI, and scikit-learn.

---

# Key Business KPIs

| KPI | Value |
|---|---:|
| Total Delivered Orders | {total_orders} |
| Total Revenue | {total_revenue} |
| GMV | {gmv} |
| Average Order Value | {average_order_value} |
| Average Review Score | {average_review_score} |
| Late Delivery % | {late_delivery_percentage} |
| Low Review % | {low_review_percentage} |

---

# Key Findings

## Revenue
The best revenue month was **{best_month_text}**.
The top revenue product category was **{top_category_text}**.
The top customer state by revenue was **{top_state_text}**.

## Customer Segmentation
The highest revenue RFM segment was **{top_rfm_segment_text}**.

## Predictive Analytics
The best low-review prediction model was **{best_model_text}** with ROC-AUC of **{best_auc}**.
"""

    final_project_summary = f"""# Final Project Summary

## Tools Used
- Python (Pandas, NumPy, Scikit-Learn)
- PostgreSQL (Prisma Cloud Warehouse)
- Power BI Desktop
- Git / GitHub

## End-to-End Workflow
Raw CSV Data → Python Cleaning → PostgreSQL Relational Schema → Fact & Dimension Views → Power BI Dashboards → Scikit-Learn Predictive Pipeline.
"""

    final_resume_bullets = f"""# Resume Impact Points

- **End-to-End Data Pipeline:** Engineerd a robust data analytics solution utilizing Python and PostgreSQL to ingest, clean, and relationalize {total_orders} raw order transactions.
- **Advanced SQL / Warehouse Architecture:** Designed optimized Star-Schema data models within cloud PostgreSQL with indexing and complex multi-table analytical views.
- **Customer Intelligence Segmentations:** Created a custom Recency, Frequency, Monetary (RFM) cohort framework segmenting users to unlock hyper-targeted retention strategies.
- **Predictive Machine Learning Engineering:** Built a production-grade binary classification pipeline using scikit-learn to predict delivery satisfaction, achieving a model ROC-AUC of {best_auc}.
"""

    github_checklist = """# GitHub Upload Checklist

- [ ] Add `.env` to `.gitignore` to secure database strings.
- [ ] Upload database schemas and indexing files under `/sql`.
- [ ] Push clean data generation steps and modeling code under `/src`.
- [ ] Save the Power BI project template (`.pbit` or `.pbix`) in root.
- [ ] Complete the primary `README.md` showcasing the key metrics and visual summaries.
"""

    FINAL_EXECUTIVE_SUMMARY.write_text(final_executive_summary, encoding="utf-8")
    FINAL_PROJECT_SUMMARY.write_text(final_project_summary, encoding="utf-8")
    FINAL_RESUME_BULLETS.write_text(final_resume_bullets, encoding="utf-8")
    GITHUB_CHECKLIST.write_text(github_checklist, encoding="utf-8")

    print(f"Created: {FINAL_EXECUTIVE_SUMMARY}")
    print(f"Created: {FINAL_PROJECT_SUMMARY}")
    print(f"Created: {FINAL_RESUME_BULLETS}")
    print(f"Created: {GITHUB_CHECKLIST}")

    print_section("Day 10 Completed")


if __name__ == "__main__":
    generate_final_outputs()