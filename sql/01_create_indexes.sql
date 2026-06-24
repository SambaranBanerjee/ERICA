CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON olist.customers (customer_id);

CREATE INDEX IF NOT EXISTS idx_customers_unique_id ON olist.customers (customer_unique_id);

CREATE INDEX IF NOT EXISTS idx_customers_state ON olist.customers (customer_state);

CREATE INDEX IF NOT EXISTS idx_orders_order_id ON olist.orders (order_id);

CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON olist.orders (customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_status ON olist.orders (order_status);

CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp ON olist.orders (order_purchase_timestamp);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON olist.order_items (order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON olist.order_items (product_id);

CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON olist.order_items (seller_id);

CREATE INDEX IF NOT EXISTS idx_payments_order_id ON olist.payments (order_id);

CREATE INDEX IF NOT EXISTS idx_reviews_order_id ON olist.reviews (order_id);

CREATE INDEX IF NOT EXISTS idx_reviews_score ON olist.reviews (review_score);

CREATE INDEX IF NOT EXISTS idx_products_product_id ON olist.products (product_id);

CREATE INDEX IF NOT EXISTS idx_products_category ON olist.products (product_category_name_english);

CREATE INDEX IF NOT EXISTS idx_sellers_seller_id ON olist.sellers (seller_id);

CREATE INDEX IF NOT EXISTS idx_sellers_state ON olist.sellers (seller_state);