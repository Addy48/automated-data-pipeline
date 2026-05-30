# Data dictionary

## Bronze (`raw/`)

| Column | Type | Notes |
|--------|------|--------|
| Date | datetime | Session date |
| Ticker | string | yfinance symbol (`BRK-B` not `BRK.B`) |
| Security | string | Company name |
| GICS_Sector | string | GICS sector |
| GICS_Sub_Industry | string | GICS sub-industry |
| Open, High, Low, Close | float | Adjusted OHLCV close > 0 |
| Volume | int | Shares; null filled to 0 in Silver |

## Silver (`processed/`)

Bronze after null handling, type coercion, and drop of `Close <= 0`.

## Gold (`analytics/`)

Silver plus:

| Column | Type | Notes |
|--------|------|--------|
| Daily_Return | float | Percent change in Close; NaN on first bar per ticker |
| MA_20 | float | 20-session SMA; NaN until 20 bars |
| MA_50 | float | 50-session SMA; NaN until 50 bars |
| Cumulative_Return | float | Percent vs first Close in the window |
| Volatility_30D | float | 30-session stdev of Daily_Return; >= 0 |
| Max_Drawdown | float | Percent vs rolling 252-session peak; <= 0 |

Hive partitions: `year=YYYY/month=MM`.
