DROP VIEW IF EXISTS olist.pbi_executive_kpis CASCADE;

DROP VIEW IF EXISTS olist.pbi_monthly_revenue CASCADE;

DROP VIEW IF EXISTS olist.pbi_category_performance CASCADE;

DROP VIEW IF EXISTS olist.pbi_state_performance CASCADE;

DROP VIEW IF EXISTS olist.pbi_delivery_performance CASCADE;

DROP VIEW IF EXISTS olist.pbi_review_delay_impact CASCADE;

DROP VIEW IF EXISTS olist.pbi_customer_rfm_base CASCADE;

DROP VIEW IF EXISTS olist.pbi_fact_orders CASCADE;

DROP VIEW IF EXISTS olist.pbi_fact_order_items CASCADE;

CREATE VIEW olist.pbi_fact_orders AS SELECT * FROM olist.fact_orders;

CREATE VIEW olist.pbi_fact_order_items AS
SELECT *
FROM olist.fact_order_items;

CREATE VIEW olist.pbi_executive_kpis AS
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(total_revenue)::NUMERIC, 2) AS total_revenue,
    ROUND(SUM(total_freight)::NUMERIC, 2) AS total_freight,
    ROUND(SUM(total_order_value)::NUMERIC, 2) AS gmv,
    ROUND(
        (SUM(total_revenue) / NULLIF(COUNT(DISTINCT order_id), 0))::NUMERIC,
        2
    ) AS average_order_value,
    ROUND(AVG(review_score)::NUMERIC, 2) AS average_review_score,
    ROUND(
        (100.0 * SUM(is_late_delivery) / NULLIF(SUM(CASE WHEN is_delivered = TRUE THEN 1 ELSE 0 END), 0))::NUMERIC,
        2
    ) AS late_delivery_percentage,
    ROUND(
        (100.0 * SUM(is_on_time_delivery) / NULLIF(SUM(CASE WHEN is_delivered = TRUE THEN 1 ELSE 0 END), 0))::NUMERIC,
        2
    ) AS on_time_delivery_percentage,
    ROUND(
        (100.0 * SUM(is_low_review) / NULLIF(COUNT(review_score), 0))::NUMERIC,
        2
    ) AS low_review_percentage
FROM olist.fact_orders
WHERE order_status = 'delivered';

CREATE VIEW olist.pbi_monthly_revenue AS
SELECT
    purchase_year_month,
    MIN(order_purchase_timestamp)::DATE AS month_start_date,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(price)::NUMERIC, 2) AS total_revenue,
    ROUND(SUM(freight_value)::NUMERIC, 2) AS total_freight,
    ROUND(SUM(item_total_value)::NUMERIC, 2) AS gmv,
    ROUND(
        (SUM(price) / NULLIF(COUNT(DISTINCT order_id), 0))::NUMERIC,
        2
    ) AS average_order_value
FROM olist.fact_order_items
WHERE order_status = 'delivered'
GROUP BY purchase_year_month
ORDER BY purchase_year_month;

CREATE VIEW olist.pbi_category_performance AS
SELECT
    product_category_name_english,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_items_sold,
    ROUND(SUM(price)::NUMERIC, 2) AS total_revenue,
    ROUND(SUM(freight_value)::NUMERIC, 2) AS total_freight,
    ROUND(AVG(price)::NUMERIC, 2) AS average_item_price,
    ROUND(
        (SUM(price) / NULLIF(COUNT(DISTINCT order_id), 0))::NUMERIC,
        2
    ) AS average_order_value
FROM olist.fact_order_items
WHERE order_status = 'delivered'
GROUP BY product_category_name_english
ORDER BY total_revenue DESC;

CREATE VIEW olist.pbi_state_performance AS
SELECT
    customer_state,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_unique_id) AS unique_customers,
    ROUND(SUM(total_revenue)::NUMERIC, 2) AS total_revenue,
    ROUND(SUM(total_freight)::NUMERIC, 2) AS total_freight,
    ROUND(
        (SUM(total_revenue) / NULLIF(COUNT(DISTINCT order_id), 0))::NUMERIC,
        2
    ) AS average_order_value,
    ROUND(AVG(review_score)::NUMERIC, 2) AS average_review_score
FROM olist.fact_orders
WHERE order_status = 'delivered'
GROUP BY customer_state
ORDER BY total_revenue DESC;

CREATE VIEW olist.pbi_delivery_performance AS
SELECT
    customer_state,
    COUNT(DISTINCT order_id) AS delivered_orders,
    ROUND(AVG(delivery_time_days)::NUMERIC, 2) AS average_delivery_time_days,
    ROUND(AVG(estimated_delivery_time_days)::NUMERIC, 2) AS average_estimated_delivery_time_days,
    ROUND(AVG(delivery_delay_days)::NUMERIC, 2) AS average_delay_days,
    ROUND(
        (100.0 * SUM(is_late_delivery) / NULLIF(COUNT(DISTINCT order_id), 0))::NUMERIC,
        2
    ) AS late_delivery_percentage,
    ROUND(
        (100.0 * SUM(is_on_time_delivery) / NULLIF(COUNT(DISTINCT order_id), 0))::NUMERIC,
        2
    ) AS on_time_delivery_percentage,
    ROUND(AVG(review_score)::NUMERIC, 2) AS average_review_score
FROM olist.fact_orders
WHERE is_delivered = TRUE
GROUP BY customer_state
ORDER BY late_delivery_percentage DESC;

CREATE VIEW olist.pbi_review_delay_impact AS
SELECT
    CASE
        WHEN delivery_delay_days IS NULL THEN 'Unknown'
        WHEN delivery_delay_days <= 0 THEN 'On time / Early'
        WHEN delivery_delay_days BETWEEN 1 AND 3 THEN '1-3 days late'
        WHEN delivery_delay_days BETWEEN 4 AND 7 THEN '4-7 days late'
        WHEN delivery_delay_days BETWEEN 8 AND 15 THEN '8-15 days late'
        ELSE 'More than 15 days late'
    END AS delay_bucket,
    COUNT(*) AS total_reviews,
    ROUND(AVG(review_score)::NUMERIC, 2) AS average_review_score,
    ROUND(
        (100.0 * SUM(is_low_review) / NULLIF(COUNT(*), 0))::NUMERIC,
        2
    ) AS low_review_percentage,
    ROUND(
        (100.0 * SUM(is_high_review) / NULLIF(COUNT(*), 0))::NUMERIC,
        2
    ) AS high_review_percentage
FROM olist.fact_reviews
GROUP BY delay_bucket
ORDER BY average_review_score DESC;

CREATE VIEW olist.pbi_customer_rfm_base AS
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        MAX(order_purchase_timestamp::DATE) AS last_purchase_date,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(total_revenue)::NUMERIC, 2) AS monetary
    FROM olist.fact_orders
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id
),
reference_date AS (
    SELECT
        MAX(order_purchase_timestamp::DATE) + INTERVAL '1 day' AS analysis_date
    FROM olist.fact_orders
)
SELECT
    co.customer_unique_id,
    co.last_purchase_date,
    DATE_PART('day', rd.analysis_date - co.last_purchase_date)::INT AS recency_days,
    co.frequency,
    co.monetary
FROM customer_orders co
CROSS JOIN reference_date rd
ORDER BY monetary DESC;