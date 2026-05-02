import csv
import json
import argparse
from tabulate import tabulate
import matplotlib.pyplot as plt


# ---------- Student Class ----------
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def average(self):
        return sum(self.marks.values()) / len(self.marks)

    def grade(self):
        avg = self.average()
        return (
            "A" if avg >= 90 else
            "B" if avg >= 75 else
            "C"
        )


# ---------- Load CSV ----------
def load_students(file_path):
    students = []

    try:
        with open(file_path) as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row.pop("name")

                # handle missing values safely
                marks = {
                    k: int(v) if v != "" else 0
                    for k, v in row.items()
                }

                students.append(Student(name, marks))

    except Exception as e:
        print("Error:", e)

    return students


# ---------- Process ----------
def process(students):
    results = []

    for s in students:
        results.append({
            "name": s.name,
            "average": round(s.average(), 2),
            "grade": s.grade(),
            "marks": s.marks
        })

    return results


# ---------- Ranking ----------
def rank_students(results):
    return sorted(results, key=lambda x: x["average"], reverse=True)


# ---------- Subject Toppers ----------
def subject_toppers(results):
    subjects = results[0]["marks"].keys()
    toppers = {}

    for sub in subjects:
        toppers[sub] = max(results, key=lambda x: x["marks"][sub])

    return toppers


# ---------- Save JSON ----------
def save_json(results):
    with open("report.json", "w") as f:
        json.dump(results, f, indent=4)

    print("\nReport saved as report.json")


# ---------- Pretty Table ----------
def print_table(results):
    table = []

    for r in results:
        table.append([r["name"], r["average"], r["grade"]])

    print(tabulate(table, headers=["Name", "Average", "Grade"]))


# ---------- Plot ----------
def plot_averages(results):
    names = [r["name"] for r in results]
    avgs = [r["average"] for r in results]

    fig, ax = plt.subplots()
    ax.bar(names, avgs)
    ax.set_title("Student Performance")
    ax.set_xlabel("Students")
    ax.set_ylabel("Average Marks")

    plt.show()


# ---------- CLI ----------
def get_args():
    parser = argparse.ArgumentParser(description="Student Grade Tracker")

    parser.add_argument("file", help="CSV file path")
    parser.add_argument("--export", action="store_true", help="Export JSON")
    parser.add_argument("--plot", action="store_true", help="Show graph")

    return parser.parse_args()


# ---------- Main ----------
if __name__ == "__main__":
    args = get_args()

    students = load_students(args.file)

    if not students:
        print("No data found!")
        exit()

    results = process(students)

    ranked = rank_students(results)

    print("\n🏆 Rankings:")
    print_table(ranked)

    toppers = subject_toppers(results)

    print("\n🎯 Subject Toppers:")
    for sub, top in toppers.items():
        print(f"{sub}: {top['name']} ({top['marks'][sub]})")

    if args.export:
        save_json(ranked)

    if args.plot:
        plot_averages(ranked)