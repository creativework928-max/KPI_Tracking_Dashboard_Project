-- Executive KPI query
SELECT
    SUM(Revenue) AS gross_revenue,
    COUNT(DISTINCT InvoiceNo) AS orders,
    SUM(Quantity) AS units_sold,
    COUNT(DISTINCT CustomerID) AS active_customers,
    SUM(Revenue) / NULLIF(COUNT(DISTINCT InvoiceNo),0) AS average_order_value,
    SUM(Revenue) / NULLIF(COUNT(DISTINCT CustomerID),0) AS revenue_per_customer
FROM fact_sales;

-- Monthly revenue and growth
WITH monthly AS (
    SELECT Month, SUM(Revenue) revenue
    FROM fact_sales
    GROUP BY Month
)
SELECT
    Month,
    revenue,
    (revenue / LAG(revenue) OVER (ORDER BY Month) - 1) * 100 AS monthly_growth_pct
FROM monthly
ORDER BY Month;
