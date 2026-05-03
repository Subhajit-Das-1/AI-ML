"""
Student Marks Analyzer
======================
Phase 1 ML Roadmap Project — covers:
  - OOP (Phase 0)
  - File I/O: CSV + JSON (Phase 0)
  - NumPy: vectorized ops, axis-wise mean (Phase 1)
  - Pandas: load, filter, groupby, apply (Phase 1)
  - Statistics: mean, std, percentile, correlation (Phase 1)
  - Lambda: grade assignment (Phase 0)

Usage:
  python student_marks_analyzer.py
"""

import csv
import json
import random
import numpy as np
import pandas as pd


# ─────────────────────────────────────────────
# STEP 1 — Generate sample CSV data
# ─────────────────────────────────────────────

def generate_sample_csv(filepath="students.csv", n=30, seed=42):
    """
    Creates a realistic sample CSV with n students.
    Columns: name, math, physics, english, attendance
    """
    random.seed(seed)
    np.random.seed(seed)

    first_names = [
        "Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Ananya", "Dev",
        "Kavya", "Arjun", "Meera", "Rahul", "Divya", "Siddharth", "Pooja",
        "Karan", "Ishaan", "Riya", "Aditya", "Nisha", "Varun", "Tanvi",
        "Harsh", "Simran", "Nikhil", "Shreya", "Arun", "Pallavi", "Yash",
        "Deepika", "Akash"
    ]

    rows = []
    for name in first_names[:n]:
        # Normally distributed scores, clipped to 0–100
        math       = int(np.clip(np.random.normal(72, 15), 30, 100))
        physics    = int(np.clip(np.random.normal(68, 18), 30, 100))
        english    = int(np.clip(np.random.normal(75, 12), 30, 100))
        attendance = int(np.clip(np.random.normal(80,  10), 40, 100))
        rows.append([name, math, physics, english, attendance])

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "math", "physics", "english", "attendance"])
        writer.writerows(rows)

    print(f"✔  Sample CSV created → {filepath}  ({n} students)")
    return filepath


# ─────────────────────────────────────────────
# STEP 2 — Analyzer class (OOP + Pandas + NumPy)
# ─────────────────────────────────────────────

class MarksAnalyzer:
    """
    Loads a student CSV and provides:
      - summary statistics
      - grade assignment
      - top/bottom performers
      - subject correlation matrix
      - full JSON report export
    """

    SUBJECT_COLS = ["math", "physics", "english"]

    def __init__(self, filepath):
        self.filepath = filepath
        self.df = pd.read_csv(filepath)
        self._validate()
        print(f"\n✔  Loaded '{filepath}'  →  {self.df.shape[0]} students, "
              f"{self.df.shape[1]} columns")

    # ── validation ──────────────────────────────

    def _validate(self):
        required = {"name", "math", "physics", "english", "attendance"}
        missing  = required - set(self.df.columns)
        if missing:
            raise ValueError(f"CSV is missing columns: {missing}")

    # ── feature engineering ──────────────────────

    def compute_averages(self):
        """Add 'avg' column = mean across all three subjects (NumPy axis op)."""
        subject_matrix = self.df[self.SUBJECT_COLS].to_numpy()          # NumPy
        self.df["avg"] = np.mean(subject_matrix, axis=1).round(2)       # axis=1 → row-wise
        return self

    def assign_grades(self):
        """Assign letter grade using a lambda + apply pipeline."""
        if "avg" not in self.df.columns:
            self.compute_averages()

        grade_fn = lambda avg: (
            "A+" if avg >= 90 else
            "A"  if avg >= 80 else
            "B"  if avg >= 70 else
            "C"  if avg >= 60 else
            "D"
        )
        self.df["grade"] = self.df["avg"].apply(grade_fn)
        return self   # enables method chaining

    def flag_attendance_risk(self):
        """Flag students with attendance below 75% — risk of missing exams."""
        self.df["at_risk"] = self.df["attendance"] < 75
        return self

    # ── statistics ───────────────────────────────

    def summary_stats(self):
        """
        Returns a dict with per-subject statistics.
        Covers: mean, median, std, min, max, 25th/75th percentile.
        """
        stats = {}
        for col in self.SUBJECT_COLS + ["avg", "attendance"]:
            arr = self.df[col].to_numpy()
            stats[col] = {
                "mean"  : round(float(np.mean(arr)),   2),
                "median": round(float(np.median(arr)), 2),
                "std"   : round(float(np.std(arr)),    2),
                "min"   : round(float(np.min(arr)),    2),
                "max"   : round(float(np.max(arr)),    2),
                "p25"   : round(float(np.percentile(arr, 25)), 2),
                "p75"   : round(float(np.percentile(arr, 75)), 2),
            }
        return stats

    def grade_distribution(self):
        """Count of students in each grade bucket."""
        return self.df["grade"].value_counts().sort_index().to_dict()

    def subject_correlation(self):
        """
        Pearson correlation matrix between subjects.
        Value close to 1  → subjects move together (student good at both).
        Value close to 0  → no relationship.
        Value close to -1 → inverse relationship.
        """
        corr = self.df[self.SUBJECT_COLS].corr().round(3)
        return corr.to_dict()

    # ── filtering ────────────────────────────────

    def top_performers(self, n=5):
        """Top n students by average score."""
        return (self.df
                .nlargest(n, "avg")
                [["name", "math", "physics", "english", "avg", "grade"]]
                .reset_index(drop=True))

    def bottom_performers(self, n=5):
        """Bottom n students who may need extra support."""
        return (self.df
                .nsmallest(n, "avg")
                [["name", "math", "physics", "english", "avg", "grade"]]
                .reset_index(drop=True))

    def at_risk_students(self):
        """Students with low attendance."""
        if "at_risk" not in self.df.columns:
            self.flag_attendance_risk()
        return (self.df[self.df["at_risk"]]
                [["name", "avg", "grade", "attendance"]]
                .sort_values("attendance")
                .reset_index(drop=True))

    def students_by_grade(self, grade):
        """Filter all students with a specific grade."""
        return self.df[self.df["grade"] == grade][["name", "avg", "attendance"]]

    # ── groupby aggregation ──────────────────────

    def stats_by_grade(self):
        """
        GroupBy example: average of each subject per grade.
        This is the bread-and-butter Pandas aggregation pattern.
        """
        return (self.df
                .groupby("grade")[self.SUBJECT_COLS + ["avg"]]
                .agg(["mean", "count"])
                .round(2))

    # ── export ───────────────────────────────────

    def export_report(self, path="report.json"):
        """
        Exports a full analysis report to JSON.
        Combines: statistics, grade dist, top/bottom performers.
        """
        if "grade" not in self.df.columns:
            self.assign_grades()

        report = {
            "source_file"       : self.filepath,
            "total_students"    : int(len(self.df)),
            "summary_stats"     : self.summary_stats(),
            "grade_distribution": self.grade_distribution(),
            "top_5_performers"  : self.top_performers(5).to_dict(orient="records"),
            "bottom_5_performers": self.bottom_performers(5).to_dict(orient="records"),
            "at_risk_count"     : int(self.df.get("at_risk", pd.Series([False]*len(self.df))).sum()),
            "correlation_matrix": self.subject_correlation(),
        }

        with open(path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n✔  Report exported → {path}")
        return path

    def export_processed_csv(self, path="students_processed.csv"):
        """Save the enriched DataFrame (with avg, grade, at_risk) back to CSV."""
        self.df.to_csv(path, index=False)
        print(f"✔  Processed CSV saved → {path}")
        return path


# ─────────────────────────────────────────────
# STEP 3 — Pretty printer helpers
# ─────────────────────────────────────────────

def print_section(title):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")

def print_stats_table(stats):
    header = f"{'Subject':<12} {'Mean':>6} {'Median':>8} {'Std':>6} {'Min':>5} {'Max':>5} {'P25':>6} {'P75':>6}"
    print(header)
    print("·" * len(header))
    for subject, s in stats.items():
        print(f"{subject:<12} {s['mean']:>6} {s['median']:>8} "
              f"{s['std']:>6} {s['min']:>5} {s['max']:>5} "
              f"{s['p25']:>6} {s['p75']:>6}")


# ─────────────────────────────────────────────
# STEP 4 — Main runner
# ─────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Student Marks Analyzer — Phase 1 ML Project")
    print("=" * 50)

    # 1. Generate data
    csv_path = generate_sample_csv("students.csv", n=30)

    # 2. Build analyzer and run the pipeline (method chaining)
    analyzer = (MarksAnalyzer(csv_path)
                .compute_averages()
                .assign_grades()
                .flag_attendance_risk())

    # 3. Summary statistics
    print_section("Summary Statistics")
    stats = analyzer.summary_stats()
    print_stats_table(stats)

    # 4. Grade distribution
    print_section("Grade Distribution")
    for grade, count in sorted(analyzer.grade_distribution().items()):
        bar = "█" * count
        print(f"  {grade:>2}  {bar}  ({count})")

    # 5. Top performers
    print_section("Top 5 Performers")
    print(analyzer.top_performers(5).to_string(index=False))

    # 6. Bottom performers
    print_section("Bottom 5 — Need Support")
    print(analyzer.bottom_performers(5).to_string(index=False))

    # 7. At-risk students
    print_section("Attendance At-Risk (< 75%)")
    at_risk = analyzer.at_risk_students()
    if at_risk.empty:
        print("  No students below 75% attendance.")
    else:
        print(at_risk.to_string(index=False))

    # 8. Stats grouped by grade
    print_section("Average Scores by Grade")
    print(analyzer.stats_by_grade().to_string())

    # 9. Correlation matrix
    print_section("Subject Correlation Matrix")
    corr_df = pd.DataFrame(analyzer.subject_correlation()).round(3)
    print(corr_df.to_string())
    print("\n  Interpretation:")
    print("  > 0.7  = strong positive (students tend to score similarly in both)")
    print("  0.3–0.7 = moderate relationship")
    print("  < 0.3  = weak/no relationship")

    # 10. Export
    print_section("Exporting Files")
    analyzer.export_report("report.json")
    analyzer.export_processed_csv("students_processed.csv")

    print("\n✅  Analysis complete!")
    print("   Files generated: students.csv, students_processed.csv, report.json\n")


if __name__ == "__main__":
    main()
