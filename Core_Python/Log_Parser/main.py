import re
import argparse
import json
from collections import Counter
import matplotlib.pyplot as plt


# ---------- Regex Pattern ----------
LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+) "
    r"(?P<message>.+)"
)


# ---------- Load Logs ----------
def load_logs(file_path):
    try:
        with open(file_path, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        print("Error: File not found!")
        return []


# ---------- Parse Logs ----------
def parse_logs(lines):
    parsed = []
    skipped = 0

    for line in lines:
        match = LOG_PATTERN.match(line.strip())
        if match:
            data = match.groupdict()
            parsed.append({
                "timestamp": f"{data['date']} {data['time']}",
                "level": data["level"],
                "message": data["message"]
            })
        else:
            skipped += 1

    if skipped:
        print(f"Skipped {skipped} malformed lines")

    return parsed


# ---------- Analyze ----------
def analyze(parsed, top_n=3):
    if not parsed:
        print("No valid logs found!")
        return {}, []

    # Count levels
    levels = [log["level"] for log in parsed]
    level_count = Counter(levels)

    print("\nLog Level Counts:")
    for k, v in level_count.items():
        print(f"{k}: {v}")

    # Extract timestamps
    timestamps = [log["timestamp"] for log in parsed]

    # Errors
    errors = [log for log in parsed if log["level"] == "ERROR"]

    error_msgs = [e["message"] for e in errors]
    freq = Counter(error_msgs)

    print(f"\nTop {top_n} Errors:")
    for msg, count in freq.most_common(top_n):
        print(f"{msg}: {count}")

    return level_count, freq


# ---------- Export ----------
def export_json(level_count, freq):
    report = {
        "level_counts": dict(level_count),
        "top_errors": dict(freq)
    }

    with open("log_report.json", "w") as f:
        json.dump(report, f, indent=4)

    print("\nReport saved as log_report.json")


# ---------- Plot ----------
def plot_levels(level_count):
    if not level_count:
        print("Nothing to plot")
        return

    fig, ax = plt.subplots()
    ax.bar(level_count.keys(), level_count.values())
    ax.set_title("Log Level Distribution")
    ax.set_xlabel("Level")
    ax.set_ylabel("Count")

    plt.show()


# ---------- CLI ----------
def get_args():
    parser = argparse.ArgumentParser(description="Log Parser Tool")

    parser.add_argument("file", help="Path to log file")
    parser.add_argument("--top", type=int, default=3, help="Top N errors")
    parser.add_argument("--export", action="store_true", help="Export JSON report")
    parser.add_argument("--plot", action="store_true", help="Plot log levels")

    return parser.parse_args()


# ---------- Main ----------
if __name__ == "__main__":
    args = get_args()

    lines = load_logs(args.file)
    parsed = parse_logs(lines)

    level_count, freq = analyze(parsed, args.top)

    if args.export:
        export_json(level_count, freq)

    if args.plot:
        plot_levels(level_count)