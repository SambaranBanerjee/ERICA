import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from config import BASE_DIR, PROCESSED_DATA_DIR


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "olist")

DATABASE_DIR = BASE_DIR / "database"


TABLE_FILES = {
    "customers": "customers_clean.csv",
    "sellers": "sellers_clean.csv",
    "orders": "orders_clean.csv",
    "order_items": "order_items_clean.csv",
    "payments": "payments_clean.csv",
    "reviews": "reviews_clean.csv",
    "products": "products_clean.csv",
    "product_categories": "product_categories_clean.csv",
    "geolocation": "geolocation_clean.csv",
}


DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "reviews": ["review_creation_date", "review_answer_timestamp"],
}


BOOLEAN_COLUMNS = {
    "orders": ["is_delivered"],
}


def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def get_engine():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing. Add it to your .env file.")

    return create_engine(DATABASE_URL, pool_pre_ping=True)


def validate_processed_files() -> None:
    print_section("Validating Processed CSV Files")

    missing_files = []

    for file_name in TABLE_FILES.values():
        file_path = PROCESSED_DATA_DIR / file_name
        if not file_path.exists():
            missing_files.append(file_name)

    if missing_files:
        print("Missing processed files:")
        for file_name in missing_files:
            print(f"  - {file_name}")

        raise FileNotFoundError(
            "Run python src/clean_data.py before creating the PostgreSQL warehouse."
        )

    print("All processed files are available.")


def create_schema(engine) -> None:
    print_section("Creating Schema")

    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{POSTGRES_SCHEMA}";'))

    print(f"Schema ready: {POSTGRES_SCHEMA}")


def prepare_dataframe(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in DATE_COLUMNS.get(table_name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in BOOLEAN_COLUMNS.get(table_name, []):
        if col in df.columns:
            df[col] = df[col].astype("bool")

    df = df.where(pd.notnull(df), None)

    return df


def load_tables_to_postgres(engine) -> None:
    print_section("Loading Cleaned CSV Files Into Online PostgreSQL")

    for table_name, file_name in TABLE_FILES.items():
        file_path = PROCESSED_DATA_DIR / file_name

        print(f"Loading {file_name} into {POSTGRES_SCHEMA}.{table_name}...")

        df = pd.read_csv(file_path)
        df = prepare_dataframe(table_name, df)

        df.to_sql(
            name=table_name,
            con=engine,
            schema=POSTGRES_SCHEMA,
            if_exists="replace",
            index=False,
            chunksize=5000,
            method="multi",
        )

        print(f"Loaded {table_name:<20} rows={df.shape[0]:,} columns={df.shape[1]}")


def execute_sql_file(engine, file_name: str) -> None:
    file_path = DATABASE_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    sql = file_path.read_text(encoding="utf-8")

    print(f"Executing {file_name}...")

    with engine.begin() as conn:
        conn.execute(text(sql))

    print(f"Completed {file_name}")


def validate_loaded_tables(engine) -> None:
    print_section("Validating Loaded PostgreSQL Tables")

    with engine.begin() as conn:
        for table_name in TABLE_FILES.keys():
            result = conn.execute(
                text(f'SELECT COUNT(*) FROM "{POSTGRES_SCHEMA}"."{table_name}";')
            )
            row_count = result.scalar()
            print(f"{POSTGRES_SCHEMA}.{table_name:<20} rows={row_count:,}")


def validate_views(engine) -> None:
    print_section("Validating Analytics Views")

    views = [
        "fact_orders",
        "fact_order_items",
        "fact_payments",
        "fact_reviews",
        "dim_customers",
        "dim_products",
        "dim_sellers",
        "dim_date",
        "pbi_executive_kpis",
        "pbi_monthly_revenue",
        "pbi_category_performance",
        "pbi_state_performance",
        "pbi_delivery_performance",
        "pbi_review_delay_impact",
        "pbi_customer_rfm_base",
    ]

    with engine.begin() as conn:
        for view_name in views:
            result = conn.execute(
                text(f'SELECT COUNT(*) FROM "{POSTGRES_SCHEMA}"."{view_name}";')
            )
            row_count = result.scalar()
            print(f"{POSTGRES_SCHEMA}.{view_name:<30} rows={row_count:,}")


def main() -> None:
    print_section("Day 3: Online PostgreSQL Warehouse Setup Started")

    validate_processed_files()

    engine = get_engine()

    create_schema(engine)
    load_tables_to_postgres(engine)

    execute_sql_file(engine, "01_create_indexes.sql")
    execute_sql_file(engine, "02_create_analytics_views.sql")
    execute_sql_file(engine, "03_create_powerbi_views.sql")

    validate_loaded_tables(engine)
    validate_views(engine)

    print_section("Day 3 Completed")
    print("Online PostgreSQL warehouse created successfully.")


if __name__ == "__main__":
    main()