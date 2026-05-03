"""
Student Marks Visualizer
========================
Companion to student_marks_analyzer.py

Charts covered:
  1. Bar chart       — average score per subject
  2. Histogram       — score distribution (with KDE)
  3. Box plot        — spread & outliers per subject
  4. Heatmap         — correlation matrix
  5. Scatter plot    — math vs english (attendance as color)
  6. Count plot      — grade distribution
  7. Violin plot     — score distribution shape per grade
  8. Line plot       — sorted averages (ranking view)

Run: python student_visualizer.py
Saves all charts to: charts/
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import matplotlib
matplotlib.use("Agg")   # non-interactive backend — no GUI, no Qt warnings

# ─────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────

os.makedirs("charts", exist_ok=True)

# Seaborn theme — apply ONCE at the top
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

SUBJECTS = ["math", "physics", "english"]
PALETTE  = {"A+": "#1D9E75", "A": "#378ADD", "B": "#7F77DD",
            "C": "#EF9F27", "D": "#E24B4A"}


# ─────────────────────────────────────────────
# Generate + load data  (reuses logic from analyzer)
# ─────────────────────────────────────────────

def build_dataframe(seed=42, n=30):
    rng = np.random.default_rng(seed)
    names = [
        "Aarav","Priya","Rohan","Sneha","Vikram","Ananya","Dev","Kavya",
        "Arjun","Meera","Rahul","Divya","Siddharth","Pooja","Karan","Ishaan",
        "Riya","Aditya","Nisha","Varun","Tanvi","Harsh","Simran","Nikhil",
        "Shreya","Arun","Pallavi","Yash","Deepika","Akash"
    ]
    df = pd.DataFrame({
        "name"      : names[:n],
        "math"      : rng.normal(72, 15, n).clip(30, 100).astype(int),
        "physics"   : rng.normal(68, 18, n).clip(30, 100).astype(int),
        "english"   : rng.normal(75, 12, n).clip(30, 100).astype(int),
        "attendance": rng.normal(80, 10, n).clip(40, 100).astype(int),
    })
    df["avg"] = df[SUBJECTS].mean(axis=1).round(2)
    df["grade"] = df["avg"].apply(
        lambda x: "A+" if x>=90 else "A" if x>=80 else
                  "B"  if x>=70 else "C" if x>=60 else "D"
    )
    return df

df = build_dataframe()


# ─────────────────────────────────────────────
# Helper — save with tight layout
# ─────────────────────────────────────────────

def save(fig, filename):
    fig.tight_layout()
    path = f"charts/{filename}"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {path}")


# ─────────────────────────────────────────────
# Chart 1 — Bar chart: average per subject
# ─────────────────────────────────────────────

def chart_bar_averages(df):
    """
    When to use: compare a single metric across categories.
    Key params: x=category, y=value, errorbar shows std dev.
    """
    # Melt wide → long format so seaborn can group by subject
    long = df[SUBJECTS].melt(var_name="Subject", value_name="Score")

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        data=long,
        x="Subject", y="Score",
        hue="Subject",
        palette=["#378ADD", "#7F77DD", "#1D9E75"],
        legend=False,
        errorbar="sd",          # show standard deviation as error bar
        capsize=0.1,
        ax=ax
    )
    ax.set_title("Average score per subject (with std dev)", fontweight="bold")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(20))
    save(fig, "1_bar_averages.png")


# ─────────────────────────────────────────────
# Chart 2 — Histogram + KDE: score distribution
# ─────────────────────────────────────────────

def chart_histogram(df):
    """
    When to use: understand the shape of a single variable.
    KDE (kernel density estimate) smooths the histogram into a curve.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=False)
    colors = ["#378ADD", "#7F77DD", "#1D9E75"]

    for ax, subject, color in zip(axes, SUBJECTS, colors):
        sns.histplot(
            df[subject],
            bins=10,
            kde=True,               # overlay smooth density curve
            color=color,
            alpha=0.7,
            ax=ax
        )
        ax.axvline(df[subject].mean(), color="red",
                   linestyle="--", linewidth=1.2, label="mean")
        ax.set_title(subject.capitalize())
        ax.set_xlabel("Score")
        ax.legend(fontsize=9)

    fig.suptitle("Score distribution per subject", fontweight="bold", y=1.02)
    save(fig, "2_histograms.png")


# ─────────────────────────────────────────────
# Chart 3 — Box plot: spread & outliers
# ─────────────────────────────────────────────

def chart_boxplot(df):
    """
    When to use: show median, IQR (interquartile range), and outliers at a glance.
    The box = middle 50% of data. Whiskers = 1.5×IQR. Dots = outliers.
    """
    long = df[SUBJECTS].melt(var_name="Subject", value_name="Score")

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(
        data=long,
        x="Subject", y="Score",
        hue="Subject", legend=False,
        palette=["#378ADD", "#7F77DD", "#1D9E75"],
        width=0.5,
        flierprops={"marker": "o", "markerfacecolor": "red",
                    "markersize": 6, "alpha": 0.6},   # outlier style
        ax=ax
    )
    ax.set_title("Score spread per subject — box plot", fontweight="bold")
    ax.set_ylabel("Score")
    save(fig, "3_boxplot.png")


# ─────────────────────────────────────────────
# Chart 4 — Heatmap: correlation matrix
# ─────────────────────────────────────────────

def chart_heatmap(df):
    """
    When to use: visualize pairwise correlations between multiple variables.
    Values close to 1 = strong positive, -1 = strong negative, 0 = no relationship.
    In ML: helps identify redundant features before training.
    """
    corr = df[SUBJECTS + ["attendance", "avg"]].corr().round(2)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        corr,
        annot=True,             # show numbers inside cells
        fmt=".2f",
        cmap="coolwarm",        # blue = negative, red = positive
        center=0,               # 0 correlation = white
        vmin=-1, vmax=1,
        square=True,
        linewidths=0.5,
        ax=ax
    )
    ax.set_title("Correlation matrix — all variables", fontweight="bold")
    save(fig, "4_heatmap.png")


# ─────────────────────────────────────────────
# Chart 5 — Scatter plot: math vs english
# ─────────────────────────────────────────────

def chart_scatter(df):
    """
    When to use: explore relationship between two continuous variables.
    Color = attendance %, size = constant here (can encode a 3rd variable).
    regression line (regplot) shows the trend.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    sc = ax.scatter(
        df["math"], df["english"],
        c=df["attendance"],         # color encodes attendance
        cmap="RdYlGn",              # red = low, green = high attendance
        s=80, alpha=0.85, edgecolors="white", linewidths=0.5
    )
    # Regression trend line (no scatter, just the line)
    sns.regplot(
        data=df, x="math", y="english",
        scatter=False,
        line_kws={"color": "#378ADD", "linewidth": 1.5, "linestyle": "--"},
        ax=ax
    )
    cbar = fig.colorbar(sc, ax=ax, shrink=0.8)
    cbar.set_label("Attendance %", fontsize=10)

    ax.set_xlabel("Math score")
    ax.set_ylabel("English score")
    ax.set_title("Math vs English — coloured by attendance", fontweight="bold")
    save(fig, "5_scatter.png")


# ─────────────────────────────────────────────
# Chart 6 — Count plot: grade distribution
# ─────────────────────────────────────────────

def chart_grade_counts(df):
    """
    When to use: count occurrences of categorical values.
    Equivalent to a bar chart of value_counts().
    """
    grade_order = ["A+", "A", "B", "C", "D"]
    present = [g for g in grade_order if g in df["grade"].unique()]

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.countplot(
        data=df,
        x="grade",
        hue="grade", legend=False,
        order=present,
        palette=[PALETTE[g] for g in present],
        ax=ax
    )
    # Annotate bar heights
    for bar in ax.patches:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.2,
                    str(int(h)), ha="center", va="bottom", fontsize=11)

    ax.set_title("Grade distribution", fontweight="bold")
    ax.set_xlabel("Grade")
    ax.set_ylabel("Number of students")
    save(fig, "6_grade_counts.png")


# ─────────────────────────────────────────────
# Chart 7 — Violin plot: avg score by grade
# ─────────────────────────────────────────────

def chart_violin(df):
    """
    When to use: like a box plot but also shows the probability density.
    Wide = many students at that score. Narrow = few.
    Great for seeing if a grade group clusters tightly or spreads out.
    """
    grade_order = [g for g in ["A+","A","B","C","D"]
                   if g in df["grade"].unique()]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.violinplot(
        data=df,
        x="grade", y="avg",
        hue="grade", legend=False,
        order=grade_order,
        palette=[PALETTE[g] for g in grade_order],
        inner="box",            # show mini box plot inside violin
        cut=0,                  # don't extend beyond data range
        ax=ax
    )
    ax.set_title("Average score distribution by grade — violin plot",
                 fontweight="bold")
    ax.set_xlabel("Grade")
    ax.set_ylabel("Average score")
    save(fig, "7_violin.png")


# ─────────────────────────────────────────────
# Chart 8 — Line plot: student ranking
# ─────────────────────────────────────────────

def chart_ranking(df):
    """
    When to use: show a metric sorted by rank.
    Useful for seeing the gap between top and bottom performers.
    """
    ranked = df.sort_values("avg", ascending=False).reset_index(drop=True)
    ranked["rank"] = ranked.index + 1

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(ranked["rank"], ranked["avg"],
            color="#378ADD", linewidth=2, marker="o",
            markersize=5, markerfacecolor="white", markeredgewidth=1.5)

    # Color-band the grade zones
    ax.axhspan(90, 100, alpha=0.08, color="#1D9E75", label="A+")
    ax.axhspan(80,  90, alpha=0.08, color="#378ADD", label="A")
    ax.axhspan(70,  80, alpha=0.08, color="#7F77DD", label="B")
    ax.axhspan(60,  70, alpha=0.08, color="#EF9F27", label="C")
    ax.axhspan(0,   60, alpha=0.08, color="#E24B4A", label="D")

    ax.set_title("Student ranking by average score", fontweight="bold")
    ax.set_xlabel("Rank")
    ax.set_ylabel("Average score")
    ax.set_xlim(0.5, len(ranked) + 0.5)
    ax.legend(loc="upper right", fontsize=9, title="Grade zone")
    save(fig, "8_ranking.png")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("=" * 45)
    print("  Student Marks Visualizer")
    print("=" * 45)
    print(f"\nDataset: {len(df)} students\n")

    chart_bar_averages(df)
    chart_histogram(df)
    chart_boxplot(df)
    chart_heatmap(df)
    chart_scatter(df)
    chart_grade_counts(df)
    chart_violin(df)
    chart_ranking(df)

    print(f"\n✅  8 charts saved to charts/")
    print("    Open any .png to view.\n")


if __name__ == "__main__":
    main()
