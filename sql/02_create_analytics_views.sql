DROP VIEW IF EXISTS olist.fact_reviews CASCADE;

DROP VIEW IF EXISTS olist.fact_payments CASCADE;

DROP VIEW IF EXISTS olist.fact_order_items CASCADE;

DROP VIEW IF EXISTS olist.fact_orders CASCADE;

DROP VIEW IF EXISTS olist.dim_date CASCADE;

DROP VIEW IF EXISTS olist.dim_sellers CASCADE;

DROP VIEW IF EXISTS olist.dim_products CASCADE;

DROP VIEW IF EXISTS olist.dim_customers CASCADE;

CREATE VIEW olist.dim_customers AS
SELECT DISTINCT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM olist.customers;

CREATE VIEW olist.dim_products AS
SELECT DISTINCT
    product_id,
    product_category_name,
    product_category_name_english,
    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    product_volume_cm3
FROM olist.products;

CREATE VIEW olist.dim_sellers AS
SELECT DISTINCT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM olist.sellers;

CREATE VIEW olist.dim_date AS
SELECT DISTINCT
    CAST(order_purchase_timestamp AS DATE) AS date_key,
    EXTRACT(YEAR FROM order_purchase_timestamp)::INT AS year,
    EXTRACT(MONTH FROM order_purchase_timestamp)::INT AS month,
    EXTRACT(DAY FROM order_purchase_timestamp)::INT AS day,
    TO_CHAR(order_purchase_timestamp, 'YYYY-MM') AS year_month,
    TO_CHAR(order_purchase_timestamp, 'Month') AS month_name,
    EXTRACT(QUARTER FROM order_purchase_timestamp)::INT AS quarter
FROM olist.orders
WHERE order_purchase_timestamp IS NOT NULL;

CREATE VIEW olist.fact_order_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    o.purchase_year,
    o.purchase_month,
    o.purchase_year_month,
    oi.price,
    oi.freight_value,
    oi.item_total_value,
    oi.freight_percentage,
    p.product_category_name,
    p.product_category_name_english,
    s.seller_city,
    s.seller_state,
    c.customer_city,
    c.customer_state,
    o.delivery_time_days,
    o.estimated_delivery_time_days,
    o.delivery_delay_days,
    o.is_delivered,
    o.is_late_delivery,
    o.is_on_time_delivery
FROM
    olist.order_items oi
    LEFT JOIN olist.orders o ON oi.order_id = o.order_id
    LEFT JOIN olist.customers c ON o.customer_id = c.customer_id
    LEFT JOIN olist.products p ON oi.product_id = p.product_id
    LEFT JOIN olist.sellers s ON oi.seller_id = s.seller_id;

CREATE VIEW olist.fact_orders AS
WITH
    order_revenue AS (
        SELECT
            order_id,
            SUM(price) AS total_revenue,
            SUM(freight_value) AS total_freight,
            SUM(item_total_value) AS total_order_value,
            COUNT(*) AS total_items
        FROM olist.order_items
        GROUP BY
            order_id
    ),
    review_per_order AS (
        SELECT
            order_id,
            AVG(review_score) AS review_score,
            MAX(is_low_review) AS is_low_review,
            MAX(is_high_review) AS is_high_review,
            MAX(has_review_comment) AS has_review_comment
        FROM olist.reviews
        GROUP BY
            order_id
    )
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    o.purchase_year,
    o.purchase_month,
    o.purchase_year_month,
    o.delivery_time_days,
    o.estimated_delivery_time_days,
    o.delivery_delay_days,
    o.is_delivered,
    o.is_late_delivery,
    o.is_on_time_delivery,
    c.customer_city,
    c.customer_state,
    COALESCE(orv.total_revenue, 0) AS total_revenue,
    COALESCE(orv.total_freight, 0) AS total_freight,
    COALESCE(orv.total_order_value, 0) AS total_order_value,
    COALESCE(orv.total_items, 0) AS total_items,
    r.review_score,
    r.is_low_review,
    r.is_high_review,
    r.has_review_comment
FROM
    olist.orders o
    LEFT JOIN olist.customers c ON o.customer_id = c.customer_id
    LEFT JOIN order_revenue orv ON o.order_id = orv.order_id
    LEFT JOIN review_per_order r ON o.order_id = r.order_id;

CREATE VIEW olist.fact_payments AS
SELECT p.order_id, p.payment_sequential, p.payment_type, p.payment_installments, p.payment_value, p.is_installment_payment, o.customer_id, c.customer_unique_id, o.order_status, o.order_purchase_timestamp, o.purchase_year, o.purchase_month, o.purchase_year_month
FROM olist.payments p
    LEFT JOIN olist.orders o ON p.order_id = o.order_id
    LEFT JOIN olist.customers c ON o.customer_id = c.customer_id;

CREATE VIEW olist.fact_reviews AS
SELECT
    r.review_id,
    r.order_id,
    r.review_score,
    r.review_comment_title,
    r.review_comment_message,
    r.review_creation_date,
    r.review_answer_timestamp,
    r.has_review_comment,
    r.is_low_review,
    r.is_high_review,
    o.customer_id,
    c.customer_unique_id,
    o.order_status,
    o.delivery_delay_days,
    o.delivery_time_days,
    o.is_late_delivery,
    o.is_on_time_delivery,
    o.purchase_year_month,
    c.customer_city,
    c.customer_state
FROM olist.reviews r
    LEFT JOIN olist.orders o ON r.order_id = o.order_id
    LEFT JOIN olist.customers c ON o.customer_id = c.customer_id;