-- 1. Top 5 funds by AUM from scheme performance
SELECT amfi_code, scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for each fund
SELECT d.year, d.month, n.amfi_code, f.scheme_name, AVG(n.nav) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date_id = d.date_id
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY d.year, d.month, n.amfi_code
ORDER BY d.year, d.month, avg_nav DESC;

-- 3. YoY SIP amount growth by month
WITH monthly_sip AS (
    SELECT d.year, d.month, SUM(amount_inr) AS total_sip_inr
    FROM fact_transactions t
    JOIN dim_date d ON t.date_id = d.date_id
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year, d.month
)
SELECT current.year, current.month,
       current.total_sip_inr AS sip_current_year,
       prior.total_sip_inr AS sip_prior_year,
       CASE WHEN prior.total_sip_inr = 0 THEN NULL
            ELSE ROUND((current.total_sip_inr - prior.total_sip_inr) / prior.total_sip_inr * 100, 2)
       END AS yoy_growth_pct
FROM monthly_sip current
LEFT JOIN monthly_sip prior
  ON current.month = prior.month
  AND current.year = prior.year + 1
ORDER BY current.year, current.month;

-- 4. Transaction counts and total amount by state
SELECT state,
       COUNT(*) AS transaction_count,
       SUM(amount_inr) AS total_amount_inr,
       SUM(CASE WHEN transaction_type = 'SIP' THEN amount_inr ELSE 0 END) AS sip_amount_inr,
       SUM(CASE WHEN transaction_type = 'Redemption' THEN amount_inr ELSE 0 END) AS redemption_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratios outside the expected 0.1%-2.5% range
SELECT amfi_code, scheme_name, fund_house, expense_ratio_pct
FROM fact_performance
WHERE expense_ratio_within_expected = 0
ORDER BY expense_ratio_pct DESC;

-- 6. Top 10 funds by 3-year return
SELECT amfi_code, scheme_name, fund_house, return_3yr_pct
FROM fact_performance
ORDER BY return_3yr_pct DESC
LIMIT 10;

-- 7. Average monthly AUM by fund house
SELECT a.fund_house, d.year, d.month, AVG(a.aum_crore) AS avg_aum_crore
FROM fact_aum a
JOIN dim_date d ON a.date_id = d.date_id
GROUP BY a.fund_house, d.year, d.month
ORDER BY avg_aum_crore DESC;

-- 8. Redemption share by fund
SELECT f.amfi_code, f.scheme_name, f.fund_house,
       SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount_inr ELSE 0 END) AS redemption_amount_inr,
       SUM(t.amount_inr) AS total_amount_inr,
       ROUND(SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount_inr ELSE 0 END) * 100.0 / SUM(t.amount_inr), 2) AS redemption_share_pct
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
GROUP BY f.amfi_code
HAVING SUM(t.amount_inr) > 0
ORDER BY redemption_share_pct DESC
LIMIT 20;

-- 9. Funds with the highest NAV volatility (calculated standard deviation)
SELECT n.amfi_code,
       f.scheme_name,
       f.fund_house,
       ROUND(SQRT(AVG(n.nav * n.nav) - AVG(n.nav) * AVG(n.nav)), 4) AS nav_stddev
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
GROUP BY n.amfi_code
ORDER BY nav_stddev DESC
LIMIT 10;

-- 10. Current-year transaction volume by KYC status
SELECT d.year, t.kyc_status, COUNT(*) AS transaction_count, SUM(amount_inr) AS total_amount_inr
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
GROUP BY d.year, t.kyc_status
ORDER BY d.year DESC, total_amount_inr DESC;
