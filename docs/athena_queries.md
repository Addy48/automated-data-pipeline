# Athena examples

Replace the table suffix with the partition you loaded.

```sql
-- Top 10 by cumulative return
SELECT ticker, gics_sector, MAX(cumulative_return) AS max_return
FROM sp500_analytics.sp500_anl_2026_05
GROUP BY ticker, gics_sector
ORDER BY max_return DESC
LIMIT 10;

-- Sector average return and volatility
SELECT gics_sector,
       ROUND(AVG(cumulative_return), 2) AS avg_return,
       ROUND(AVG(volatility_30d), 2) AS avg_volatility
FROM sp500_analytics.sp500_anl_2026_05
GROUP BY gics_sector
ORDER BY avg_return DESC;
```
