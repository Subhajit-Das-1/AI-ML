# Concepts practiced:

# Time series line plots
# Multi-line charts (multiple countries/states)
# Annotations (marking peaks, lockdowns)
# Rolling averages to smooth noise
# Date formatting on x-axis

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# ✅ Load the correct CSV from your project
df = pd.read_csv("full_grouped.csv", parse_dates=["Date"])

# ✅ Column names match full_grouped.csv exactly
# Columns: Date, Country/Region, Confirmed, Deaths, Recovered, Active,
#          New cases, New deaths, New recovered, WHO Region

fig, ax = plt.subplots(figsize=(14, 6))

countries = ["India", "US", "Brazil"]   # ✅ "US" not "USA" — matches the CSV value
colors   = ["#FF6B35", "#4A90D9", "#27AE60"]

for country, color in zip(countries, colors):
    data = df[df["Country/Region"] == country].copy()
    data = data.sort_values("Date")

    # ✅ Use 7-day rolling average on "New cases" column
    data["smoothed"] = data["New cases"].rolling(7, min_periods=1).mean()

    ax.plot(data["Date"], data["smoothed"],
            label=country, color=color, linewidth=2)

# ✅ Formatting
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.xticks(rotation=45)

ax.set_title("COVID-19 New Cases (7-Day Rolling Avg)", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Daily New Cases", fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, linestyle="--")

plt.tight_layout()
plt.show()