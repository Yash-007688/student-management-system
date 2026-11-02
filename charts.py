"""
charts.py
---------
Matplotlib Pyplot visual analytics module for CBSE Class 12 IP Project.
100% Real-Time Database / CSV Driven:
- Line Chart (Student's subject marks comparison across syllabus subjects)
- Bar Chart (Vertical individual marks & horizontal toppers leaderboard)
- Histogram (Actual class marks frequency distribution)
- Scatter Plot (Physics vs Mathematics correlation from student records)
- Box Plot (True subject-wise marks dispersion with Matplotlib 3.11+ compatibility)
- Pie Chart (Real-time pass / compartment / fail and fees status breakdown)
- Multiple subplots on one figure (2x2 dashboard strictly generated from live data)
"""

import matplotlib.pyplot as plt
import numpy as np
import database
import data_analysis


# ── 1. Bar Chart: Individual Student Marks ───────────────────────────────────

def plot_student_marks(roll_no):
    """
    Vertical Bar Chart showing marks obtained in each subject.
    Covers: Bar chart, colors, labels, title, limits, text annotations, passing benchmark.
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

    colors = ['#2980b9' if s >= 33 else '#e74c3c' for s in scores]

    plt.figure(figsize=(9, 5))
    bars = plt.bar(subjects, scores, color=colors, width=0.55, edgecolor='black', linewidth=1)

    # Benchmark lines
    plt.axhline(33, color='red', linestyle='--', linewidth=1.5, label='Passing Threshold (33)')
    avg_score = res.get("percentage", 0)
    plt.axhline(avg_score, color='green', linestyle=':', linewidth=1.8, label=f'Overall Percentage ({avg_score}%)')

    plt.ylim(0, 110)
    plt.title(f"Subject-Wise Performance: {student.get('name')} (Roll No: {roll_no})\nTotal: {res.get('total')}/500 | Grade: {res.get('grade')} | Status: {res.get('status')}",
              fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Subjects", fontsize=11, fontweight='bold')
    plt.ylabel("Marks Scored (Max 100)", fontsize=11, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., h + 1.5, f"{int(h)}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()
    return True


# ── 2. Line Chart: Student Subject Scores Profile ───────────────────────────

def plot_progress_line_chart(roll_no="101"):
    """
    Line Chart displaying a student's actual scores across subjects compared with class average.
    100% sourced from real database records.
    """
    res = database.get_result(roll_no)
    if not res or not res.get("has_marks"):
        print(f"\n[!] Cannot plot: No marks found for Roll Number '{roll_no}'.")
        return False

    student_name = res["student"]["name"]
    subjects = ["Physics", "Chemistry", "Maths", "English", "CS/IP"]
    keys = ["physics", "chemistry", "maths", "english", "cs_ip"]
    student_scores = [res["marks"].get(k, 0) for k in keys]

    # Calculate real class averages
    df = data_analysis.get_current_df()
    col_map = {"physics": "Physics", "chemistry": "Chemistry", "maths": "Maths", "english": "English", "cs_ip": "CS_IP"}
    class_avgs = [round(df[col_map[k]].mean(), 1) if col_map[k] in df.columns else 0 for k in keys]

    plt.figure(figsize=(9, 5))
    plt.plot(subjects, student_scores, marker='o', markersize=9, color='#2980b9', linestyle='-', linewidth=2.5, label=f'{student_name} Scores')
    plt.plot(subjects, class_avgs, marker='s', markersize=8, color='#e67e22', linestyle='--', linewidth=2, label='Class Average Score')

    plt.title(f"Subject Score Profile vs Class Average — {student_name} ({roll_no})", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Board Subjects", fontsize=11, fontweight='bold')
    plt.ylabel("Marks Obtained (Max 100)", fontsize=11, fontweight='bold')
    plt.ylim(0, 110)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='lower right')

    for i, txt in enumerate(student_scores):
        plt.annotate(f"{int(txt)}", (subjects[i], student_scores[i] + 2), fontweight='bold', ha='center')

    plt.tight_layout()
    plt.show()
    return True


# ── 3. Histogram: Marks Frequency Distribution ──────────────────────────────

def plot_marks_histogram():
    """
    Histogram showing actual distribution of student percentages stored in database.
    Strictly uses real dataset without any synthetic score injection.
    """
    df = data_analysis.get_current_df()
    scores = df["Percentage"].dropna().tolist()

    if not scores:
        print("\n[!] No student percentage records available to plot histogram.")
        return False

    bins = [30, 40, 50, 60, 70, 80, 90, 100]

    plt.figure(figsize=(9, 5))
    n, actual_bins, patches = plt.hist(scores, bins=bins, color='#3498db', edgecolor='black', linewidth=1.2, rwidth=0.85)

    plt.title(f"Class Percentage Frequency Distribution Histogram (Live Evaluated: {len(scores)} students)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Score Range (Percentage Bins)", fontsize=11, fontweight='bold')
    plt.ylabel("Number of Students", fontsize=11, fontweight='bold')
    plt.xticks(bins)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for i in range(len(patches)):
        h = patches[i].get_height()
        if h > 0:
            plt.text(patches[i].get_x() + patches[i].get_width() / 2., h + 0.05, f"{int(h)}", ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.show()
    return True


# ── 4. Scatter Plot: Physics vs Mathematics Correlation ──────────────────────

def plot_scatter_correlation():
    """
    Scatter Plot showing correlation between Physics and Mathematics marks from database.
    Strictly plots actual records.
    """
    df = data_analysis.get_current_df()
    valid = df.dropna(subset=["Physics", "Maths"])

    if valid.empty:
        print("\n[!] No students with both Physics and Maths marks found.")
        return False

    phy = valid["Physics"].tolist()
    math = valid["Maths"].tolist()
    names = valid["Name"].tolist()

    plt.figure(figsize=(8, 5))
    plt.scatter(phy, math, color='#e74c3c', s=100, marker='D', edgecolors='black', alpha=0.85, label='Student Scores')

    # Annotate names
    for i, name in enumerate(names):
        plt.annotate(f"{name}", (phy[i] + 0.8, math[i] + 0.8), fontsize=9)

    plt.title(f"Correlation Analysis: Physics vs Mathematics (Live: {len(valid)} students)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Physics Marks", fontsize=11, fontweight='bold')
    plt.ylabel("Mathematics Marks", fontsize=11, fontweight='bold')
    plt.xlim(min(phy) - 10, 105)
    plt.ylim(min(math) - 10, 105)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
    return True


# ── 5. Box Plot: Subject-Wise Marks Spread (Matplotlib Compatible) ───────────

def plot_subject_boxplot():
    """
    Box Plot showing median, quartiles, and dispersion of real marks per subject.
    Supports both older and newer Matplotlib versions (tick_labels / labels argument).
    """
    df = data_analysis.get_current_df()
    subjects = ["Physics", "Chemistry", "Maths", "English", "CS_IP"]

    data_to_plot = []
    active_subjects = []

    for sub in subjects:
        if sub in df.columns:
            vals = df[sub].dropna().tolist()
            if vals:
                data_to_plot.append(vals)
                active_subjects.append(sub)

    if not data_to_plot:
        print("\n[!] No subject marks found to plot box plot.")
        return False

    plt.figure(figsize=(9, 5))

    # Compatibility check for Matplotlib versions (3.9+ uses tick_labels, older uses labels)
    boxplot_kwargs = dict(
        patch_artist=True,
        boxprops=dict(facecolor='#aed6f1', color='#1b4f72', linewidth=1.5),
        medianprops=dict(color='#c0392b', linewidth=2),
        whiskerprops=dict(color='#1b4f72', linewidth=1.5),
        capprops=dict(color='#1b4f72', linewidth=1.5)
    )

    try:
        bp = plt.boxplot(data_to_plot, tick_labels=active_subjects, **boxplot_kwargs)
    except TypeError:
        bp = plt.boxplot(data_to_plot, labels=active_subjects, **boxplot_kwargs)

    plt.title("Subject Marks Spread & Dispersion (Box Plot - Live Database)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Subjects", fontsize=11, fontweight='bold')
    plt.ylabel("Marks Range (0-100)", fontsize=11, fontweight='bold')
    plt.ylim(30, 105)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()
    return True


# ── 6. Pie Chart: Result & Grade Breakdown ───────────────────────────────────

def plot_result_distribution():
    """
    Pie Chart showing percentage of Passed, Compartment, and Failed students from live DB.
    """
    df = data_analysis.get_current_df()
    status_counts = df["Status"].dropna().value_counts().to_dict()

    if not status_counts:
        print("\n[!] No evaluated results found.")
        return False

    labels = list(status_counts.keys())
    sizes = list(status_counts.values())
    color_map = {"PASSED": "#2ecc71", "COMPARTMENT": "#f39c12", "FAILED": "#e74c3c"}
    colors = [color_map.get(l, "#3498db") for l in labels]
    explode = [0.05 if l == "PASSED" else 0.0 for l in labels]

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', colors=colors,
            startangle=140, shadow=True, textprops={'fontsize': 11, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'black', 'linewidth': 1})
    plt.title(f"Class Result Distribution (Total Evaluated: {sum(sizes)})", fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()
    return True


# ── 7. Multiple Plots (Subplots: 2x2 Dashboard) ──────────────────────────────

def plot_multiple_dashboard():
    """
    Multiple Plots using plt.subplots(2, 2).
    100% strictly computed from current database DataFrame.
    """
    df = data_analysis.get_current_df()
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 1. Bar Chart: Real Subject Averages (Top-Left)
    subs = ["Phy", "Chem", "Math", "Eng", "CS"]
    sub_keys = ["Physics", "Chemistry", "Maths", "English", "CS_IP"]
    avgs = [round(df[k].mean(), 1) if k in df.columns and not np.isnan(df[k].mean()) else 0 for k in sub_keys]
    axes[0, 0].bar(subs, avgs, color='#3498db', edgecolor='black')
    axes[0, 0].set_title("1. Live Subject Averages", fontweight='bold')
    axes[0, 0].set_ylim(0, 105)
    axes[0, 0].grid(axis='y', linestyle=':')
    for i, v in enumerate(avgs):
        axes[0, 0].text(i, v + 2, f"{v}", ha='center', fontweight='bold', fontsize=9)

    # 2. Line Chart: Live Class Average vs Highest Scores (Top-Right)
    highest_scores = [df[k].max() if k in df.columns and not np.isnan(df[k].max()) else 0 for k in sub_keys]
    axes[0, 1].plot(subs, highest_scores, marker='o', color='#27ae60', linewidth=2, label='Highest Score')
    axes[0, 1].plot(subs, avgs, marker='s', color='#e67e22', linewidth=2, linestyle='--', label='Average Score')
    axes[0, 1].set_title("2. Benchmark: Max vs Average Marks", fontweight='bold')
    axes[0, 1].set_ylim(40, 105)
    axes[0, 1].grid(True, linestyle=':')
    axes[0, 1].legend(loc='lower right')

    # 3. Pie Chart: Live Gender Distribution (Bottom-Left)
    g_counts = df["Gender"].dropna().value_counts().to_dict()
    if g_counts:
        axes[1, 0].pie(list(g_counts.values()), labels=list(g_counts.keys()), autopct='%1.0f%%', colors=['#2980b9', '#e84393'])
    axes[1, 0].set_title("3. Student Gender Demographics", fontweight='bold')

    # 4. Horizontal Bar: Real Top 3 Students from Database (Bottom-Right)
    toppers = df.dropna(subset=["Percentage"]).sort_values(by="Percentage", ascending=False).head(3)
    if not toppers.empty:
        t_names = (toppers["Name"] + " (" + toppers["RollNo"].astype(str) + ")").tolist()
        t_pct = toppers["Percentage"].tolist()
        t_names.reverse()
        t_pct.reverse()
        bars = axes[1, 1].barh(t_names, t_pct, color='#2ecc71', edgecolor='black')
        axes[1, 1].set_xlim(0, 105)
        for b in bars:
            axes[1, 1].text(b.get_width() + 1, b.get_y() + b.get_height() / 2, f"{b.get_width()}%", va='center', fontweight='bold')
    axes[1, 1].set_title("4. Top Ranked Students (Live DB)", fontweight='bold')
    axes[1, 1].grid(axis='x', linestyle=':')

    fig.suptitle("CBSE Class 12 IP — Comprehensive Analytics Dashboard (100% Real-Time)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    return True


# ── 8. Real-time Leaderboard & Fees Charts ──────────────────────────────────

def plot_subject_averages():
    df = data_analysis.get_current_df()
    subjects = ["Physics", "Chemistry", "Maths", "English", "CS_IP"]
    avg_values = [round(df[s].mean(), 2) if s in df.columns and not np.isnan(df[s].mean()) else 0 for s in subjects]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(subjects, avg_values, color='#3498db', width=0.5, edgecolor='#1b4f72', linewidth=1)
    plt.ylim(0, 105)
    plt.title("Class Subject-Wise Average Performance (Real-Time)", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Subject", fontsize=11, fontweight='bold')
    plt.ylabel("Average Marks", fontsize=11, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., h + 1.5, f"{h:.1f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()


def plot_toppers(top_n=5):
    df = data_analysis.get_current_df()
    valid_df = df.dropna(subset=["Percentage"]).sort_values(by="Percentage", ascending=False).head(top_n)
    if valid_df.empty:
        print("\n[!] No students with marks records found.")
        return False

    names = (valid_df["Name"] + " (" + valid_df["RollNo"].astype(str) + ")").tolist()
    percentages = valid_df["Percentage"].tolist()
    names.reverse()
    percentages.reverse()

    plt.figure(figsize=(9, 5))
    bars = plt.barh(names, percentages, color='#2ecc71', edgecolor='#196f3d', height=0.55)
    plt.xlim(0, 110)
    plt.title(f"Top {len(names)} Students Leaderboard (Live Database)", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Percentage (%)", fontsize=11, fontweight='bold')
    plt.grid(axis='x', linestyle='--', alpha=0.5)

    for bar in bars:
        w = bar.get_width()
        plt.text(w + 1, bar.get_y() + bar.get_height() / 2., f"{w:.1f}%", ha='left', va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()


def plot_fees_distribution():
    fees_records = database.get_all_fees()
    status_counts = {"Paid": 0, "Partial": 0, "Pending": 0}
    for f in fees_records:
        st = f.get("status", "Pending")
        status_counts[st] = status_counts.get(st, 0) + 1

    labels = [f"{k} ({v})" for k, v in status_counts.items() if v > 0]
    sizes = [v for v in status_counts.values() if v > 0]
    colors = ["#27ae60", "#f39c12", "#c0392b"][:len(labels)]

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'black', 'linewidth': 1})
    plt.title("Fees Status Overview (Live Database)", fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()
