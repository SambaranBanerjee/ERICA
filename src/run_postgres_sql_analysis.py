import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

from config import BASE_DIR


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "olist")

OUTPUT_DIR = BASE_DIR / "reports" / "sql_outputs"


def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def get_engine():
    global DATABASE_URL 
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing. Add it to your .env file.")
        
    # 2. Use a local variable to handle the replacement safely
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return create_engine(url, pool_pre_ping=True)


ANALYSIS_QUERIES = {
    "executive_kpis": """
        SELECT *
        FROM olist.pbi_executive_kpis;
    """,

    "monthly_revenue": """
        SELECT *
        FROM olist.pbi_monthly_revenue
        ORDER BY month_start_date;
    """,

    "top_product_categories": """
        SELECT *
        FROM olist.pbi_category_performance
        ORDER BY total_revenue DESC
        LIMIT 15;
    """,

    "revenue_by_customer_state": """
        SELECT *
        FROM olist.pbi_state_performance
        ORDER BY total_revenue DESC;
    """,

    "delivery_performance_by_state": """
        SELECT *
        FROM olist.pbi_delivery_performance
        ORDER BY late_delivery_percentage DESC;
    """,

    "review_delay_impact": """
        SELECT *
        FROM olist.pbi_review_delay_impact;
    """,

    "payment_type_analysis": """
        SELECT
            payment_type,
            COUNT(DISTINCT order_id) AS total_orders,
            COUNT(*) AS total_payment_records,
            ROUND(SUM(payment_value)::NUMERIC, 2) AS total_payment_value,
            ROUND(AVG(payment_value)::NUMERIC, 2) AS average_payment_value,
            ROUND(AVG(payment_installments)::NUMERIC, 2) AS average_installments
        FROM olist.fact_payments
        GROUP BY payment_type
        ORDER BY total_payment_value DESC;
    """,

    "order_status_distribution": """
        SELECT
            order_status,
            COUNT(*) AS total_orders,
            ROUND(
                (100.0 * COUNT(*) / SUM(COUNT(*)) OVER ())::NUMERIC,
                2
            ) AS percentage
        FROM olist.orders
        GROUP BY order_status
        ORDER BY total_orders DESC;
    """,

    "customer_frequency_distribution": """
        WITH customer_frequency AS (
            SELECT
                customer_unique_id,
                COUNT(DISTINCT order_id) AS total_orders
            FROM olist.fact_orders
            WHERE order_status = 'delivered'
            GROUP BY customer_unique_id
        )
        SELECT
            total_orders,
            COUNT(*) AS customer_count
        FROM customer_frequency
        GROUP BY total_orders
        ORDER BY total_orders;
    """,

    "repeat_customer_rate": """
        WITH customer_frequency AS (
            SELECT
                customer_unique_id,
                COUNT(DISTINCT order_id) AS total_orders
            FROM olist.fact_orders
            WHERE order_status = 'delivered'
            GROUP BY customer_unique_id
        )
        SELECT
            COUNT(*) AS total_customers,
            SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
            ROUND(
                (100.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) / COUNT(*))::NUMERIC,
                2
            ) AS repeat_customer_percentage
        FROM customer_frequency;
    """,

    "customer_rfm_base": """
        SELECT *
        FROM olist.pbi_customer_rfm_base;
    """,

    "low_review_categories": """
        SELECT
            foi.product_category_name_english,
            COUNT(DISTINCT foi.order_id) AS reviewed_orders,
            ROUND(AVG(fr.review_score)::NUMERIC, 2) AS average_review_score,
            ROUND(
                (100.0 * SUM(fr.is_low_review) / NULLIF(COUNT(fr.review_id), 0))::NUMERIC,
                2
            ) AS low_review_percentage,
            ROUND(SUM(foi.price)::NUMERIC, 2) AS total_revenue
        FROM olist.fact_order_items foi
        LEFT JOIN olist.fact_reviews fr
            ON foi.order_id = fr.order_id
        WHERE foi.order_status = 'delivered'
        GROUP BY foi.product_category_name_english
        HAVING COUNT(DISTINCT foi.order_id) >= 100
        ORDER BY low_review_percentage DESC
        LIMIT 20;
    """,

    "delivery_delay_by_product_category": """
        SELECT
            product_category_name_english,
            COUNT(DISTINCT order_id) AS total_orders,
            ROUND(AVG(delivery_time_days)::NUMERIC, 2) AS average_delivery_time_days,
            ROUND(AVG(delivery_delay_days)::NUMERIC, 2) AS average_delay_days,
            ROUND(
                (100.0 * SUM(is_late_delivery) / NULLIF(COUNT(DISTINCT order_id), 0))::NUMERIC,
                2
            ) AS late_delivery_percentage
        FROM olist.fact_order_items
        WHERE is_delivered = TRUE
        GROUP BY product_category_name_english
        HAVING COUNT(DISTINCT order_id) >= 100
        ORDER BY late_delivery_percentage DESC
        LIMIT 20;
    """,
}


def run_queries() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    engine = get_engine()

    print_section("Day 4: Running Online PostgreSQL SQL Business Analysis")

    for query_name, query in ANALYSIS_QUERIES.items():
        print(f"Running query: {query_name}")

        df = pd.read_sql_query(query, engine)

        output_path = OUTPUT_DIR / f"{query_name}.csv"
        df.to_csv(output_path, index=False)

        print(f"Saved: {output_path}")
        print(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]}")

    print_section("Day 4 Completed")
    print(f"SQL outputs saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    run_queries()