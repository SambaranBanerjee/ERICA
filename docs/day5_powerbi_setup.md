# Day 5: Power BI Setup

## Goal

Connected Power BI Desktop to the cloud-hosted PostgreSQL database and created the first executive dashboard page.

## Data Source

Database: Online PostgreSQL / Prisma Postgres  
Schema: olist

## Imported Views

- fact_orders
- fact_order_items
- fact_payments
- fact_reviews
- dim_customers
- dim_products
- dim_sellers
- dim_date
- pbi_executive_kpis
- pbi_monthly_revenue
- pbi_category_performance
- pbi_state_performance
- pbi_delivery_performance
- pbi_review_delay_impact
- pbi_customer_rfm_base

## Relationships

- dim_customers to fact_orders
- dim_customers to fact_order_items
- dim_products to fact_order_items
- dim_sellers to fact_order_items
- dim_date to fact_orders
- dim_date to fact_order_items

## Measures Created

- Total Revenue
- Total Orders
- GMV
- Average Order Value
- Average Review Score
- Late Delivery %
- On-Time Delivery %
- Low Review %
- Unique Customers
- Repeat Customer %

## Dashboard Page Created

Executive Summary

## Visuals Created

- KPI cards
- Monthly revenue trend
- Top product categories
- Revenue by customer state
- Delivery delay impact on review score