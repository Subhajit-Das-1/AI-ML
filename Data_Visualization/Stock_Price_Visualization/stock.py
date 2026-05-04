# Raw Data
#    ↓
# Load & Parse (Pandas)
#    ↓
# Explore Shape/Types
#    ↓
# Plot Distributions     ← Seaborn histplot, boxplot
#    ↓
# Plot Trends            ← Matplotlib line charts
#    ↓
# Spot Correlations      ← Seaborn heatmap / pairplot
#    ↓
# Identify Outliers      ← Boxplots, scatter plots
#    ↓
# Ready for Modeling ✅

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf

# Download data
df = yf.download("AAPL", start="2022-01-01", end="2024-01-01", auto_adjust=True)

# ✅ Fix MultiIndex columns (yfinance v0.2+ issue)
df.columns = df.columns.get_level_values(0)

df["MA50"]  = df["Close"].rolling(50).mean()
df["MA200"] = df["Close"].rolling(200).mean()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                gridspec_kw={"height_ratios": [3, 1]})

# Price + Moving Averages
ax1.plot(df.index, df["Close"], label="Close Price", alpha=0.7, color="#2196F3")
ax1.plot(df.index, df["MA50"],  label="MA 50",  linestyle="--", color="#FF9800")
ax1.plot(df.index, df["MA200"], label="MA 200", linestyle="--", color="#F44336")
ax1.set_title("AAPL Stock Price with Moving Averages", fontsize=14, fontweight="bold")
ax1.set_ylabel("Price (USD)")
ax1.legend()
ax1.grid(True, alpha=0.3)

# ✅ KEY FIX: squeeze() converts 2D → 1D Series so bar() works
volume = df["Volume"].squeeze()
ax2.bar(df.index, volume, color="steelblue", alpha=0.5, width=1)
ax2.set_title("Trading Volume")
ax2.set_ylabel("Volume")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()