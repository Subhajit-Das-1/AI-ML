import csv
import argparse
import json
from tabulate import tabulate
import matplotlib.pyplot as plt


# ---------- Helper ----------
def is_number(val):
    if val is None or val == "":
        return False
    try:
        float(val)
        return True
    except:
        return False


# ---------- Load CSV ----------
def load_csv(file_path):
    try:
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print("Error: File not found!")
        return []
    except Exception as e:
        print("Error:", e)
        return []


# ---------- Analyze ----------
def analyze(data):
    if not data:
        print("CSV is empty or invalid!")
        return {}, 0, 0

    rows = len(data)
    columns = len(data[0])
    col_names = list(data[0].keys())

    print(f"\nRows: {rows}")
    print(f"Columns: {columns}")
    print(f"Column Names: {', '.join(col_names)}")

    numeric_cols = {
        col: [float(row[col]) for row in data if is_number(row[col])]
        for col in col_names
    }

    stats = {}

    for col, values in numeric_cols.items():
        if values:
            stats[col] = {
                "min": min(values),
                "max": max(values),
                "avg": round(sum(values) / len(values), 2),
            }

    return stats, rows, columns


# ---------- Pretty Table ----------
def print_table(stats):
    if not stats:
        print("\nNo numeric data found.")
        return

    table = []
    for col, s in stats.items():
        table.append([col, s["min"], s["max"], s["avg"]])

    print("\nStats Table:")
    print(tabulate(table, headers=["Column", "Min", "Max", "Avg"]))


# ---------- Save JSON ----------
def save_report(rows, columns, stats):
    report = {
        "rows": rows,
        "columns": columns,
        "stats": stats,
    }

    with open("report.json", "w") as f:
        json.dump(report, f, indent=4)

    print("\nReport saved as report.json")


# ---------- Plot ----------
def plot_column(data, column):
    values = [float(row[column]) for row in data if is_number(row[column])]

    if not values:
        print(f"No numeric data in column: {column}")
        return

    plt.hist(values)
    plt.title(f"{column} Distribution")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.show()


# ---------- CLI ----------
def get_args():
    parser = argparse.ArgumentParser(description="CSV Analyzer Tool")

    parser.add_argument("file", help="Path to CSV file")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    parser.add_argument("--export", action="store_true", help="Export report to JSON")
    parser.add_argument("--plot", type=str, help="Plot a specific column")

    return parser.parse_args()


# ---------- Main ----------
if __name__ == "__main__":
    args = get_args()

    data = load_csv(args.file)

    stats, rows, columns = analyze(data)

    if not args.summary:
        print_table(stats)

    if args.export:
        save_report(rows, columns, stats)

    if args.plot:
        plot_column(data, args.plot)