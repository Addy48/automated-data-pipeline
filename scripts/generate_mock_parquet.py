import pandas as pd
import numpy as np

dates = pd.date_range(start="2023-01-01", periods=30)
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

rows = []
for symbol in symbols:
    base_price = 100.0 if symbol != "AMZN" else 150.0
    for i, date in enumerate(dates):
        # Add some random walk
        price = base_price + np.random.normal(0, 1) + (i * 0.1)
        rows.append(
            {
                "Date": date.date(),
                "Symbol": symbol,
                "Open": price,
                "High": price + 2.0,
                "Low": price - 2.0,
                "Close": price + 0.5,
                "Volume": 1000 + (i * 10),
            }
        )

df = pd.DataFrame(rows)
df.to_parquet("tests/fixtures/mock_ohlcv.parquet", engine="pyarrow")
print("Successfully generated tests/fixtures/mock_ohlcv.parquet")
