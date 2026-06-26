# Business Insights Report

## Project

E-Commerce Revenue & Customer Intelligence Analytics Platform

## Data Source

Cloud-hosted PostgreSQL warehouse created from the Olist e-commerce dataset.

---

# 1. Executive Summary

The marketplace processed **96,478 delivered orders** with total product revenue of **13,221,498.11** and GMV of **15,419,773.75**.

The average order value was **137.04**.

Customer satisfaction performance:

- Average review score: **4.14**
- Low review percentage: **13.20%**
- On-time delivery percentage: **93.22%**
- Late delivery percentage: **6.77%**

---

# 2. Revenue Insights

## Best Revenue Month

The highest revenue month was **2017-11** with revenue of **987,765.37**.

## Lowest Revenue Month

The lowest revenue month was **2016-12** with revenue of **10.90**.

## Top Product Category

The highest revenue category was **health beauty**, generating **1,233,131.72** from **8,647 orders**.

## Top Customer State

The highest revenue customer state was **SP**, generating **5,067,633.16**.

---

# 3. Delivery Performance Insights

The state with the highest late delivery percentage was **AL**, with a late delivery rate of **21.41%**.

This state should be investigated for logistics bottlenecks, seller distribution issues, or last-mile delivery problems.

---

# 4. Review and Satisfaction Insights

The delay bucket with the best review score was **On time / Early**, with an average review score of **4.28**.

The delay bucket with the worst review score was **8-15 days late**, with an average review score of **1.68**.

This confirms that delivery performance is connected to customer satisfaction.

The product category with the highest low-review percentage was **office furniture**, with a low-review rate of **25.63%**.

---

# 5. Business Recommendations

## Recommendation 1: Improve delivery performance in high-delay states

Observation:
Some customer states show significantly higher late-delivery percentages.

Business Impact:
Late deliveries reduce customer satisfaction and increase the probability of low review scores.

Action:
Prioritize logistics review for states with the highest late-delivery percentage.

Expected Outcome:
Improved review scores and better customer retention.

---

## Recommendation 2: Focus marketing on high-revenue categories

Observation:
A small number of product categories contribute a large share of revenue.

Business Impact:
Prioritizing high-performing categories can improve marketing ROI.

Action:
Run category-specific campaigns for the top revenue categories.

Expected Outcome:
Higher conversion rate and improved monthly revenue.

---

## Recommendation 3: Investigate low-review product categories

Observation:
Some categories have higher low-review percentages even with meaningful order volume.

Business Impact:
Poor ratings can reduce future conversions and customer trust.

Action:
Analyze seller quality, product descriptions, delivery time, and return issues for these categories.

Expected Outcome:
Lower complaint rate and improved customer satisfaction.

---

## Recommendation 4: Track KPIs weekly

Leadership should monitor:

- Total Revenue
- Total Orders
- Average Order Value
- On-Time Delivery %
- Late Delivery %
- Average Review Score
- Low Review %
- Revenue by Category
- Revenue by State

---

# 6. Dashboard Pages Created

- Executive Summary
- Revenue Analysis
- Delivery Performance
- Review Analysis
- Customer RFM Analysis

---

# 7. Resume Impact

This project demonstrates:

- Python data cleaning
- PostgreSQL cloud warehouse loading
- SQL analytics
- Power BI dashboarding
- KPI design
- Customer segmentation
- Business recommendation writing
