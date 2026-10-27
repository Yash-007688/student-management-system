"""
charts.py
---------
Matplotlib Pyplot visual analytics module for Student Management System.
Features:
1. Individual student subject-wise marks bar chart with average benchmark.
2. Class performance & subject averages comparison chart.
3. Top students leaderboard bar chart.
4. Pass / Compartment / Fail distribution pie chart.
5. Fees collection status pie chart.
"""

import matplotlib.pyplot as plt
import database


def plot_student_marks(roll_no):
    """
    Bar chart showing subject-wise marks of a specific student.
    """
    res = database.get_result(roll_no)
    if not res:
        print(f"\n[!] Error: No student found with Roll Number '{roll_no}'.")
        return False
    if not res.get("has_marks"):
        print(f"\n[!] Marks not yet entered for Roll Number '{roll_no}'.")
        return False

    student = res["student"]
    marks = res["marks"]
    subjects = ["Physics", "Chemistry", "Maths", "English", "CS/IP"]
    scores = [
        marks.get("physics", 0),
        marks.get("chemistry", 0),
        marks.get("maths", 0),
        marks.get("english", 0),
        marks.get("cs_ip", 0),
    ]

    colors = ['#2b5c8f' if s >= 33 else '#d9534f' for s in scores]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(subjects, scores, color=colors, width=0.55, edgecolor='black', linewidth=1)

    # Passing mark line
    plt.axhline(33, color='red', linestyle='--', linewidth=1.2, label='Passing Mark (33)')
    
    # Student average line
    avg_score = res.get("percentage", 0)
    plt.axhline(avg_score, color='green', linestyle=':', linewidth=1.5, label=f'Student Avg ({avg_score}%)')

    plt.ylim(0, 105)
    plt.title(f"Academic Performance: {student.get('name')} (Roll No: {roll_no})\nTotal: {res.get('total')}/500 | Grade: {res.get('grade')} | Status: {res.get('status')}", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Subjects", fontsize=11, fontweight='bold')
    plt.ylabel("Marks Obtained (Max 100)", fontsize=11, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Display values on top of bars
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., h + 1.5, f"{int(h)}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()
    return True


def plot_subject_averages():
    """
    Bar chart showing average score obtained by all students across subjects.
    """
    students = database.get_all_students()
    if not students:
        print("\n[!] No students found.")
        return False

    sub_totals = {"physics": 0.0, "chemistry": 0.0, "maths": 0.0, "english": 0.0, "cs_ip": 0.0}
    count = 0

    for s in students:
        m = database.get_marks(s["roll_no"])
        if m:
            count += 1
            for k in sub_totals:
                sub_totals[k] += m.get(k, 0)

    if count == 0:
        print("\n[!] No marks data available for any students.")
        return False

    subjects = ["Physics", "Chemistry", "Maths", "English", "CS/IP"]
    avg_values = [
        round(sub_totals["physics"] / count, 2),
        round(sub_totals["chemistry"] / count, 2),
        round(sub_totals["maths"] / count, 2),
        round(sub_totals["english"] / count, 2),
        round(sub_totals["cs_ip"] / count, 2),
    ]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(subjects, avg_values, color='#3498db', width=0.5, edgecolor='#1b4f72', linewidth=1)

    plt.ylim(0, 105)
    plt.title(f"Class Subject-Wise Average Performance (Total Evaluated: {count})", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Subject", fontsize=11, fontweight='bold')
    plt.ylabel("Average Marks", fontsize=11, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., h + 1.5, f"{h:.1f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()
    return True


def plot_toppers(top_n=5):
    """
    Horizontal bar chart showing the top performing students by percentage.
    """
    students = database.get_all_students()
    records = []

    for s in students:
        res = database.get_result(s["roll_no"])
        if res and res.get("has_marks"):
            records.append({
                "name": f"{s.get('name')} ({s.get('roll_no')})",
                "percentage": res.get("percentage", 0),
                "total": res.get("total", 0)
            })

    if not records:
        print("\n[!] No students with marks records found.")
        return False

    records.sort(key=lambda x: x["percentage"], reverse=True)
    top_records = records[:top_n]
    top_records.reverse()  # To display highest on top in horizontal bar

    names = [r["name"] for r in top_records]
    percentages = [r["percentage"] for r in top_records]

    plt.figure(figsize=(9, 5))
    bars = plt.barh(names, percentages, color='#2ecc71', edgecolor='#196f3d', height=0.55)

    plt.xlim(0, 110)
    plt.title(f"Top {len(top_records)} Students Leaderboard (By Percentage)", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Percentage (%)", fontsize=11, fontweight='bold')
    plt.grid(axis='x', linestyle='--', alpha=0.5)

    for bar in bars:
        w = bar.get_width()
        plt.text(w + 1, bar.get_y() + bar.get_height() / 2., f"{w:.1f}%", ha='left', va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()
    return True


def plot_result_distribution():
    """
    Pie chart showing distribution of Pass, Compartment, and Failed students.
    """
    students = database.get_all_students()
    status_counts = {"PASSED": 0, "COMPARTMENT": 0, "FAILED": 0}
    total_evaluated = 0

    for s in students:
        res = database.get_result(s["roll_no"])
        if res and res.get("has_marks"):
            status = res.get("status", "")
            total_evaluated += 1
            if status == "PASSED":
                status_counts["PASSED"] += 1
            elif "COMPARTMENT" in status:
                status_counts["COMPARTMENT"] += 1
            else:
                status_counts["FAILED"] += 1

    if total_evaluated == 0:
        print("\n[!] No results available to plot distribution.")
        return False

    labels = []
    sizes = []
    colors = []
    color_map = {"PASSED": "#2ecc71", "COMPARTMENT": "#f39c12", "FAILED": "#e74c3c"}

    for k, v in status_counts.items():
        if v > 0:
            labels.append(f"{k} ({v})")
            sizes.append(v)
            colors.append(color_map[k])

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140,
            textprops={'fontsize': 11, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'black', 'linewidth': 1})
    plt.title(f"Class Result Distribution (Total Evaluated: {total_evaluated})", fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()
    return True


def plot_fees_distribution():
    """
    Donut / Pie chart showing Fees Payment Status.
    """
    fees_records = database.get_all_fees()
    if not fees_records:
        print("\n[!] No fees records found.")
        return False

    status_counts = {"Paid": 0, "Partial": 0, "Pending": 0}
    for f in fees_records:
        st = f.get("status", "Pending")
        status_counts[st] = status_counts.get(st, 0) + 1

    labels = []
    sizes = []
    colors = []
    c_map = {"Paid": "#27ae60", "Partial": "#f39c12", "Pending": "#c0392b"}

    for k, v in status_counts.items():
        if v > 0:
            labels.append(f"{k} ({v})")
            sizes.append(v)
            colors.append(c_map.get(k, "#95a5a6"))

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'black', 'linewidth': 1})
    plt.title("Fees Status Overview", fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()
    return True
