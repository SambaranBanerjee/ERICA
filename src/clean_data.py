from pathlib import Path
import pandas as pd
import numpy as np

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR


def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def load_csv(file_name: str) -> pd.DataFrame:
    file_path = RAW_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    return pd.read_csv(file_path)

def standardize_text_column(series: pd.Series) -> pd.Series:
    return (
        series
        .astype("string")
        .str.strip()
        .str.lower()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )


def clean_customers() -> pd.DataFrame:
    df = load_csv("olist_customers_dataset.csv")


    df = df.drop_duplicates()

    df["customer_city"] = standardize_text_column(df["customer_city"])
    df["customer_state"] = df["customer_state"].astype("string").str.strip().str.upper()

    df["customer_zip_code_prefix"] = pd.to_numeric(
        df["customer_zip_code_prefix"], errors="coerce"
    ).astype("Int64")

    return df


def clean_sellers() -> pd.DataFrame:
    df = load_csv("olist_sellers_dataset.csv")

    df = df.drop_duplicates()

    df["seller_city"] = standardize_text_column(df["seller_city"])
    df["seller_state"] = df["seller_state"].astype("string").str.strip().str.upper()

    df["seller_zip_code_prefix"] = pd.to_numeric(
        df["seller_zip_code_prefix"], errors="coerce"
    ).astype("Int64")

    return df


def clean_orders() -> pd.DataFrame:
    df = load_csv("olist_orders_dataset.csv")

    df = df.drop_duplicates()

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["order_status"] = (
        df["order_status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # Delivery features
    df["delivery_time_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    df["estimated_delivery_time_days"] = (
        df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]
    ).dt.days

    df["delivery_delay_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days

    df["is_delivered"] = df["order_status"].eq("delivered")

    df["is_late_delivery"] = np.where(
        (df["is_delivered"]) & (df["delivery_delay_days"] > 0),
        1,
        0,
    )

    df["is_on_time_delivery"] = np.where(
        (df["is_delivered"]) & (df["delivery_delay_days"] <= 0),
        1,
        0,
    )

    df["purchase_year"] = df["order_purchase_timestamp"].dt.year
    df["purchase_month"] = df["order_purchase_timestamp"].dt.month
    df["purchase_year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype("string")

    return df


def clean_order_items() -> pd.DataFrame:
    df = load_csv("olist_order_items_dataset.csv")

    df = df.drop_duplicates()

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"], errors="coerce"
    )

    numeric_columns = ["order_item_id", "price", "freight_value"]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove impossible financial records
    df = df[df["price"].notna()]
    df = df[df["freight_value"].notna()]
    df = df[df["price"] >= 0]
    df = df[df["freight_value"] >= 0]

    df["item_total_value"] = df["price"] + df["freight_value"]
    df["freight_percentage"] = np.where(
        df["price"] > 0,
        df["freight_value"] / df["price"],
        np.nan,
    )

    return df


def clean_payments() -> pd.DataFrame:
    df = load_csv("olist_order_payments_dataset.csv")

    df = df.drop_duplicates()

    df["payment_type"] = (
        df["payment_type"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    numeric_columns = [
        "payment_sequential",
        "payment_installments",
        "payment_value",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["payment_value"].notna()]
    df = df[df["payment_value"] >= 0]

    df["is_installment_payment"] = np.where(df["payment_installments"] > 1, 1, 0)

    return df


def clean_reviews() -> pd.DataFrame:
    df = load_csv("olist_order_reviews_dataset.csv")

    df = df.drop_duplicates()

    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce")

    df["review_creation_date"] = pd.to_datetime(
        df["review_creation_date"], errors="coerce"
    )

    df["review_answer_timestamp"] = pd.to_datetime(
        df["review_answer_timestamp"], errors="coerce"
    )

    df["review_comment_title"] = (
        df["review_comment_title"]
        .fillna("")
        .astype("string")
        .str.strip()
    )

    df["review_comment_message"] = (
        df["review_comment_message"]
        .fillna("")
        .astype("string")
        .str.strip()
    )

    df["has_review_comment"] = np.where(
        df["review_comment_message"].str.len() > 0,
        1,
        0,
    )

    df["is_low_review"] = np.where(df["review_score"] <= 2, 1, 0)
    df["is_high_review"] = np.where(df["review_score"] >= 4, 1, 0)

    return df


def clean_products() -> pd.DataFrame:
    products = load_csv("olist_products_dataset.csv")
    categories = load_csv("product_category_name_translation.csv")

    products = products.drop_duplicates()
    categories = categories.drop_duplicates()

    products["product_category_name"] = (
        products["product_category_name"]
        .fillna("unknown")
        .astype("string")
        .str.strip()
        .str.lower()
    )

    categories["product_category_name"] = (
        categories["product_category_name"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    categories["product_category_name_english"] = (
        categories["product_category_name_english"]
        .astype("string")
        .str.strip()
        .str.lower()
        .str.replace("_", " ", regex=False)
    )

    df = products.merge(
        categories,
        on="product_category_name",
        how="left",
    )

    df["product_category_name_english"] = (
        df["product_category_name_english"]
        .fillna("unknown")
        .astype("string")
    )

    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["product_volume_cm3"] = (
        df["product_length_cm"]
        * df["product_height_cm"]
        * df["product_width_cm"]
    )

    return df


def clean_product_categories() -> pd.DataFrame:
    df = load_csv("product_category_name_translation.csv")

    df = df.drop_duplicates()

    df["product_category_name"] = (
        df["product_category_name"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    df["product_category_name_english"] = (
        df["product_category_name_english"]
        .astype("string")
        .str.strip()
        .str.lower()
        .str.replace("_", " ", regex=False)
    )

    return df


def clean_geolocation() -> pd.DataFrame:
    df = load_csv("olist_geolocation_dataset.csv")

    df = df.drop_duplicates()

    df["geolocation_city"] = standardize_text_column(df["geolocation_city"])
    df["geolocation_state"] = df["geolocation_state"].astype("string").str.strip().str.upper()

    df["geolocation_zip_code_prefix"] = pd.to_numeric(
        df["geolocation_zip_code_prefix"], errors="coerce"
    ).astype("Int64")

    df["geolocation_lat"] = pd.to_numeric(df["geolocation_lat"], errors="coerce")
    df["geolocation_lng"] = pd.to_numeric(df["geolocation_lng"], errors="coerce")

    # Aggregate because geolocation has many duplicate ZIP prefixes
    geo_agg = (
        df.groupby(
            ["geolocation_zip_code_prefix", "geolocation_city", "geolocation_state"],
            as_index=False,
        )
        .agg(
            geolocation_lat=("geolocation_lat", "mean"),
            geolocation_lng=("geolocation_lng", "mean"),
        )
    )

    return geo_agg


def save_clean_file(df: pd.DataFrame, file_name: str) -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DATA_DIR / file_name
    df.to_csv(output_path, index=False)
    print(f"Saved {file_name}: {df.shape[0]:,} rows, {df.shape[1]} columns")


def generate_cleaning_summary(cleaned_tables: dict[str, pd.DataFrame]) -> None:
    print_section("Cleaning Summary")

    for name, df in cleaned_tables.items():
        missing_values = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        print(
            f"{name:<25} rows={df.shape[0]:>10,} | "
            f"columns={df.shape[1]:>3} | "
            f"missing_values={missing_values:>8,} | "
            f"duplicates={duplicate_rows:>5,}"
        )


def main() -> None:
    print_section("Day 2: Starting Data Cleaning Pipeline")

    cleaned_tables = {
        "customers_clean.csv": clean_customers(),
        "sellers_clean.csv": clean_sellers(),
        "orders_clean.csv": clean_orders(),
        "order_items_clean.csv": clean_order_items(),
        "payments_clean.csv": clean_payments(),
        "reviews_clean.csv": clean_reviews(),
        "products_clean.csv": clean_products(),
        "product_categories_clean.csv": clean_product_categories(),
        "geolocation_clean.csv": clean_geolocation(),
    }

    print_section("Saving Cleaned Files")

    for file_name, df in cleaned_tables.items():
        save_clean_file(df, file_name)

    generate_cleaning_summary(cleaned_tables)

    print_section("Day 2 Completed")
    print("Cleaned files are available in data/processed/")


if __name__ == "__main__":
    main()