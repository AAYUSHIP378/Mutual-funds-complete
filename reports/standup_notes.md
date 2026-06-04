# Standup Notes Tasks 5 and 6

1. Completed Task 5 dashboard generation and Task 6 advanced analytics.
2. Built `build_dashboard_reports.py` to generate dashboard page PNGs and a PDF report.
3. Generated dashboard pages in `dashboard/figures/` and assembled `dashboard/dashboard_report.pdf`.
4. Documented dashboard deliverables in `dashboard/dashboard_note.md`.
5. Updated `README.md` with dashboard generation instructions and limitations.
6. Verified that Power BI `.pbix` creation is not possible in this environment.
7. Built `build_advanced_analytics.py` for advanced risk, investor, and concentration analytics.
8. Loaded cleaned NAV history, scheme performance, investor transactions, and portfolio holdings.
9. Computed daily NAV returns for all fund schemes from `02_nav_history.csv`.
10. Calculated 95% VaR for all 40 schemes using the 5th percentile of daily returns.
11. Computed CVaR as the mean return below the VaR threshold per fund.
12. Saved VaR and CVaR analytics to `var_cvar_report.csv`.
13. Selected 5 key funds for rolling 90-day Sharpe using top scheme AUM.
14. Implemented rolling Sharpe with annualization √252 and exported `rolling_sharpe_chart.png`.
15. Built investor cohort analysis using each investor’s first SIP transaction year.
16. Calculated cohort average SIP amount, total invested, and investor count.
17. Identified top fund preference for each investor cohort and saved results.
18. Saved investor cohort analytics to `investor_cohort_report.csv`.
19. Performed SIP continuity analysis for investors with 6+ SIP transactions.
20. Computed average SIP gap days and flagged investors with gap > 35 days as “at-risk”.
21. Saved SIP continuity results to `sip_continuity_report.csv`.
22. Calculated sector HHI concentration for equity fund portfolios using share weights.
23. Filtered concentration analysis to equity-focused funds and saved `hhi_concentration_report.csv`.
24. Added `recommender.py` to deliver top 3 fund recommendations by risk appetite.
25. Implemented risk appetite mapping and Sharpe-based ranking for recommendations.
26. Created `Advanced_Analytics.ipynb` to document analytics, charts, and recommendations.
27. Included notebook sections for VaR/CVaR, rolling Sharpe, cohorts, continuity, HHI, and recommender use.
28. Logged advanced insights for risk, cohort behavior, SIP continuity, concentration, and fund selection.
29. Verified both Task 5 and Task 6 scripts completed successfully with no runtime errors.
30. Task 5 and Task 6 are complete and deliverables are ready for company update.
