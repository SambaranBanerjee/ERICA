DROP VIEW IF EXISTS olist.pbi_rfm_segments CASCADE;


CREATE VIEW olist.pbi_rfm_segments AS
WITH customer_rfm AS (
    SELECT
        customer_unique_id,
        recency_days,
        frequency,
        monetary,

        NTILE(5) OVER (ORDER BY recency_days DESC) AS recency_score_raw,
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS monetary_score
    FROM olist.pbi_customer_rfm_base
),
rfm_scored AS (
    SELECT
        customer_unique_id,
        recency_days,
        frequency,
        monetary,

-- Lower recency is better, so reverse the score
6 - recency_score_raw AS recency_score,
        frequency_score,
        monetary_score,

        CONCAT(
            (6 - recency_score_raw)::TEXT,
            frequency_score::TEXT,
            monetary_score::TEXT
        ) AS rfm_score
    FROM customer_rfm
),
rfm_segmented AS (
    SELECT
        *,
        CASE
            WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4
                THEN 'Champions'

            WHEN recency_score >= 3 AND frequency_score >= 4 AND monetary_score >= 3
                THEN 'Loyal Customers'

            WHEN recency_score >= 4 AND frequency_score BETWEEN 2 AND 3
                THEN 'Potential Loyalists'

            WHEN recency_score >= 4 AND frequency_score <= 2
                THEN 'New Customers'

            WHEN recency_score BETWEEN 2 AND 3 AND frequency_score >= 3
                THEN 'Need Attention'

            WHEN recency_score <= 2 AND frequency_score >= 3
                THEN 'At Risk Customers'

            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score >= 3
                THEN 'Cannot Lose Them'

            WHEN recency_score <= 2 AND frequency_score <= 2
                THEN 'Lost Customers'

            ELSE 'Low Value Customers'
        END AS customer_segment
    FROM rfm_scored
)
SELECT *
FROM rfm_segmented;