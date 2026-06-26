"""
Day 9: Low Review Risk Prediction

This script:
1. Connects to online PostgreSQL using DATABASE_URL
2. Pulls order, delivery, payment, category, and review data
3. Builds a low-review classification dataset
4. Trains Logistic Regression and Random Forest models
5. Evaluates performance
6. Exports predictions, metrics, feature importance, and a markdown report

Run:
    python src/train_low_review_model.py
"""

import os
import json
from pathlib import Path

import pandas as pd
import numpy as np

from sqlalchemy import create_engine
from dotenv import load_dotenv

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from config import BASE_DIR


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", "olist")

REPORTS_DIR = BASE_DIR / "reports"
MODEL_OUTPUT_DIR = REPORTS_DIR / "model_outputs"

METRICS_FILE = MODEL_OUTPUT_DIR / "low_review_model_metrics.json"
PREDICTIONS_FILE = MODEL_OUTPUT_DIR / "low_review_predictions.csv"
FEATURE_IMPORTANCE_FILE = MODEL_OUTPUT_DIR / "feature_importance.csv"
MODEL_REPORT_FILE = REPORTS_DIR / "low_review_prediction_report.md"


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


def load_model_dataset() -> pd.DataFrame:
    engine = get_engine()

    query = f"""
    WITH order_payment AS (
        SELECT
            order_id,
            SUM(payment_value) AS total_payment_value,
            AVG(payment_installments) AS avg_payment_installments,
            MAX(is_installment_payment) AS used_installment_payment
        FROM {POSTGRES_SCHEMA}.fact_payments
        GROUP BY order_id
    ),
    order_category AS (
        SELECT
            order_id,
            MAX(product_category_name_english) AS main_product_category,
            COUNT(DISTINCT product_id) AS distinct_products,
            COUNT(*) AS total_items,
            AVG(price) AS avg_item_price,
            AVG(freight_value) AS avg_freight_value,
            SUM(price) AS item_revenue,
            SUM(freight_value) AS freight_revenue
        FROM {POSTGRES_SCHEMA}.fact_order_items
        GROUP BY order_id
    )
    SELECT
        fo.order_id,
        fo.customer_state,
        fo.order_status,
        fo.purchase_month,

        fo.delivery_time_days,
        fo.estimated_delivery_time_days,
        fo.delivery_delay_days,
        fo.is_late_delivery,
        fo.is_on_time_delivery,

        fo.total_revenue,
        fo.total_freight,
        fo.total_order_value,
        fo.total_items AS order_total_items,

        fo.review_score,
        fo.is_low_review,

        oc.main_product_category,
        oc.distinct_products,
        oc.total_items,
        oc.avg_item_price,
        oc.avg_freight_value,
        oc.item_revenue,
        oc.freight_revenue,

        op.total_payment_value,
        op.avg_payment_installments,
        op.used_installment_payment
    FROM {POSTGRES_SCHEMA}.fact_orders fo
    LEFT JOIN order_category oc
        ON fo.order_id = oc.order_id
    LEFT JOIN order_payment op
        ON fo.order_id = op.order_id
    WHERE fo.order_status = 'delivered'
      AND fo.review_score IS NOT NULL
      AND fo.is_low_review IS NOT NULL;
    """

    df = pd.read_sql_query(query, engine)
    return df


def prepare_features(df: pd.DataFrame):
    target = "is_low_review"

    numeric_features = [
        "purchase_month",
        "delivery_time_days",
        "estimated_delivery_time_days",
        "delivery_delay_days",
        "is_late_delivery",
        "is_on_time_delivery",
        "total_revenue",
        "total_freight",
        "total_order_value",
        "order_total_items",
        "distinct_products",
        "total_items",
        "avg_item_price",
        "avg_freight_value",
        "item_revenue",
        "freight_revenue",
        "total_payment_value",
        "avg_payment_installments",
        "used_installment_payment",
    ]

    categorical_features = [
        "customer_state",
        "main_product_category",
    ]

    available_numeric = [col for col in numeric_features if col in df.columns]
    available_categorical = [col for col in categorical_features if col in df.columns]

    X = df[available_numeric + available_categorical].copy()
    y = df[target].astype(int)

    return X, y, available_numeric, available_categorical


def build_preprocessor(numeric_features, categorical_features):
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, numeric_features),
            ("categorical", categorical_transformer, categorical_features),
        ]
    )

    return preprocessor


def evaluate_model(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)

    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
    else:
        y_proba = y_pred

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(
            y_test,
            y_pred,
            zero_division=0,
            output_dict=True,
        ),
    }

    return metrics


def get_feature_names(preprocessor, numeric_features, categorical_features):
    feature_names = []

    feature_names.extend(numeric_features)

    try:
        onehot = (
            preprocessor
            .named_transformers_["categorical"]
            .named_steps["onehot"]
        )

        categorical_names = onehot.get_feature_names_out(categorical_features)
        feature_names.extend(categorical_names)

    except Exception:
        pass

    return feature_names


def export_feature_importance(best_model, numeric_features, categorical_features):
    preprocessor = best_model.named_steps["preprocessor"]
    classifier = best_model.named_steps["classifier"]

    feature_names = get_feature_names(
        preprocessor,
        numeric_features,
        categorical_features,
    )

    if hasattr(classifier, "feature_importances_"):
        importance_values = classifier.feature_importances_
        importance_type = "random_forest_feature_importance"

    elif hasattr(classifier, "coef_"):
        importance_values = np.abs(classifier.coef_[0])
        importance_type = "absolute_logistic_regression_coefficient"

    else:
        return pd.DataFrame()

    min_len = min(len(feature_names), len(importance_values))

    importance_df = pd.DataFrame(
        {
            "feature": feature_names[:min_len],
            "importance": importance_values[:min_len],
            "importance_type": importance_type,
        }
    ).sort_values("importance", ascending=False)

    importance_df.to_csv(FEATURE_IMPORTANCE_FILE, index=False)

    return importance_df


def generate_markdown_report(
    df,
    model_metrics,
    best_model_name,
    best_metrics,
    feature_importance,
):
    low_review_rate = df["is_low_review"].mean() * 100
    total_orders = df.shape[0]
    low_review_orders = int(df["is_low_review"].sum())

    top_features_text = ""

    if not feature_importance.empty:
        top_features = feature_importance.head(10)
        for _, row in top_features.iterrows():
            top_features_text += f"- {row['feature']}: {row['importance']:.4f}\n"
    else:
        top_features_text = "Feature importance was not available."

    # --- MAKE SURE ALL OF THIS IS INDENTED INSIDE THE FUNCTION ---
    report = f"""# Low Review Risk Prediction Report

## Objective
The goal of this analysis is to predict whether a delivered order is likely to receive a low review score.

A low review is defined as:
review_score <= 2
"""

    # Indent this line by 4 spaces!
    MODEL_REPORT_FILE.write_text(report, encoding="utf-8")

def main():
    print_section("Day 9: Low Review Risk Prediction Started")

    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_model_dataset()

    print(f"Loaded modeling dataset: {df.shape[0]:,} rows, {df.shape[1]} columns")

    if df.empty:
        raise ValueError("Modeling dataset is empty. Check PostgreSQL views and loaded data.")

    df = df.dropna(subset=["is_low_review"])

    X, y, numeric_features, categorical_features = prepare_features(df)

    print(f"Low review rate: {y.mean() * 100:.2f}%")
    print(f"Numeric features: {len(numeric_features)}")
    print(f"Categorical features: {len(categorical_features)}")

    X_train, X_test, y_train, y_test, order_train, order_test = train_test_split(
        X,
        y,
        df["order_id"],
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    logistic_preprocessor = build_preprocessor(
        numeric_features,
        categorical_features,
    )

    random_forest_preprocessor = build_preprocessor(
        numeric_features,
        categorical_features,
    )

    models = {
        "logistic_regression": Pipeline(
            steps=[
                ("preprocessor", logistic_preprocessor),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocessor", random_forest_preprocessor),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=200,
                        max_depth=12,
                        min_samples_split=10,
                        min_samples_leaf=5,
                        class_weight="balanced",
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }

    model_metrics = {}
    trained_models = {}

    for model_name, model in models.items():
        print(f"Training model: {model_name}")

        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test)

        model_metrics[model_name] = metrics
        trained_models[model_name] = model

        print(
            f"{model_name} | "
            f"Accuracy={metrics['accuracy']} | "
            f"Precision={metrics['precision']} | "
            f"Recall={metrics['recall']} | "
            f"F1={metrics['f1_score']} | "
            f"ROC-AUC={metrics['roc_auc']}"
        )

    best_model_name = max(
        model_metrics,
        key=lambda name: model_metrics[name]["roc_auc"],
    )

    best_model = trained_models[best_model_name]
    best_metrics = model_metrics[best_model_name]

    print(f"Best model: {best_model_name}")

    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    predictions = pd.DataFrame(
        {
            "order_id": order_test.values,
            "actual_low_review": y_test.values,
            "predicted_low_review": y_pred,
            "low_review_probability": y_proba,
        }
    ).sort_values("low_review_probability", ascending=False)

    predictions.to_csv(PREDICTIONS_FILE, index=False)

    feature_importance = export_feature_importance(
        best_model,
        numeric_features,
        categorical_features,
    )

    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(model_metrics, f, indent=4)

    generate_markdown_report(
        df=df,
        model_metrics=model_metrics,
        best_model_name=best_model_name,
        best_metrics=best_metrics,
        feature_importance=feature_importance,
    )

    print(f"Saved metrics: {METRICS_FILE}")
    print(f"Saved predictions: {PREDICTIONS_FILE}")
    print(f"Saved feature importance: {FEATURE_IMPORTANCE_FILE}")
    print(f"Saved report: {MODEL_REPORT_FILE}")

    print_section("Day 9 Completed")

if __name__ == "__main__":
    main()