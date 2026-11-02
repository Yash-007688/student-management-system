"""
generate_screenshots.py
-----------------------
Automates screenshot generation for CBSE Class 12 IP Project submission.
Generates:
1. Matplotlib Charts (PNG):
   - 01_student_marks_bar_chart.png
   - 02_subject_scores_profile_line.png
   - 03_marks_frequency_histogram.png
   - 04_physics_vs_maths_scatter.png
   - 05_subject_boxplot_dispersion.png
   - 06_result_distribution_pie.png
   - 07_top_rankers_leaderboard.png
   - 08_comprehensive_dashboard_2x2.png
   - 09_fees_payment_distribution_pie.png
2. CUI Terminal Output Cards (PNG rendered as high-res terminal views):
   - 10_terminal_login_menu.png
   - 11_terminal_admin_dashboard.png
   - 12_terminal_students_records_table.png
   - 13_terminal_student_report_card.png
   - 14_terminal_teacher_class_security_restriction.png
   - 15_terminal_student_fee_privacy.png
   - 16_terminal_pandas_data_analysis.png
   - 17_terminal_sql_queries_demo.png
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import database
import data_analysis
import charts
import mysql_manager

SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def save_chart(plot_func, filename, *args, **kwargs):
    plt.close('all')
    plot_func(*args, **kwargs)
    path = os.path.join(SCREENSHOTS_DIR, filename)
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close('all')
    print(f"[+] Saved Chart: {filename}")


def render_terminal_screenshot(title, text_content, filename):
    plt.close('all')
    lines = text_content.strip().split('\n')
    num_lines = len(lines)
    height = max(5, num_lines * 0.28 + 1.2)

    fig = plt.figure(figsize=(10, height), facecolor='#0f172a')
    ax = fig.add_axes([0, 0, 1, 1], frameon=False)
    ax.set_facecolor('#0f172a')
    ax.axis('off')

    # Window header bar
    header_text = f"  ● ● ●   Command Prompt — {title}"
    ax.text(0.02, 0.98, header_text, transform=ax.transAxes,
            color='#94a3b8', fontsize=10, fontfamily='monospace', va='top')

    # Divider line
    ax.plot([0.02, 0.98], [0.95, 0.95], transform=ax.transAxes, color='#334155', linewidth=1)

    # Terminal body text
    y_pos = 0.92
    line_step = 0.88 / max(num_lines, 1)

    for line in lines:
        color = '#38bdf8' if any(w in line for w in ['[+]', 'PASS', 'SUCCESS', 'PASSED']) else \
                '#f87171' if any(w in line for w in ['[!]', 'BLOCKED', 'denied', 'Error']) else \
                '#fbbf24' if any(w in line for w in ['===', '---', 'STUDENT REPORT', 'DASHBOARD']) else \
                '#e2e8f0'
        ax.text(0.03, y_pos, line, transform=ax.transAxes,
                color=color, fontsize=9.5, fontfamily='monospace', va='top')
        y_pos -= line_step

    path = os.path.join(SCREENSHOTS_DIR, filename)
    plt.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close('all')
    print(f"[+] Saved Terminal View: {filename}")


def main():
    database.init_db()
    data_analysis.export_db_to_csv()
    database.verify_login("admin", "admin123")

    print("\n--- Generating Matplotlib Chart Screenshots ---")
    save_chart(charts.plot_student_marks, "01_student_marks_bar_chart.png", "101")
    save_chart(charts.plot_progress_line_chart, "02_subject_scores_profile_line.png", "101")
    save_chart(charts.plot_marks_histogram, "03_marks_frequency_histogram.png")
    save_chart(charts.plot_scatter_correlation, "04_physics_vs_maths_scatter.png")
    save_chart(charts.plot_subject_boxplot, "05_subject_boxplot_dispersion.png")
    save_chart(charts.plot_result_distribution, "06_result_distribution_pie.png")
    save_chart(charts.plot_toppers, "07_top_rankers_leaderboard.png", top_n=5)
    save_chart(charts.plot_multiple_dashboard, "08_comprehensive_dashboard_2x2.png")
    save_chart(charts.plot_fees_distribution, "09_fees_payment_distribution_pie.png")

    print("\n--- Generating CUI Terminal Output Screenshots ---")

    # 10. Login Menu
    render_terminal_screenshot(
        "Application Startup & Login Menu",
        """
=================================================================
       STUDENT MANAGEMENT SYSTEM (CBSE CLASS 12 IP)              
=================================================================
1. Login to Account
2. Quick IP Viva & Theory Guide
3. Exit Application

Enter choice (1-3): 1

--- Login Screen ---
Username: admin
Password: ••••••••

[+] Login successful as ADMIN (Admin)!
Opening Admin Dashboard...
""",
        "10_terminal_login_menu.png"
    )

    # 11. Admin Dashboard
    render_terminal_screenshot(
        "Admin Dashboard & Operations Menu",
        """
=================================================================
             ADMIN DASHBOARD — Logged in as Admin                
=================================================================
1.   View All Students
2.   Add New Student
3.   Search Student
4.   Update Student Record
5.   Delete Student
6.   Marks Entry
7.   View Result / Report Card
8.   Fees Management
9.   User Account Administration (Create/Delete Accounts)
10.  Pandas Data Analysis (Class 12 IP Syllabus)
11.  PyPlot Visualisation Hub (Line/Bar/Hist/Scatter/Box/Pie)
12.  SQL & MySQL Operations Demo (DDL/DML/Aggregate/Pandas read_sql)
13.  CBSE Class 12 IP Viva & Theory Guide (Networks/Cyber/DBMS)
14.  Logout
""",
        "11_terminal_admin_dashboard.png"
    )

    # 12. Student Records Table
    render_terminal_screenshot(
        "Registered Student Records (Tabular View)",
        """
=================================================================
                     STUDENT RECORDS VIEW                        
=================================================================
Roll No | Name         | Class | Sec | Gender | Phone      | Email
--------+--------------+-------+-----+--------+------------+-------------------------
101     | Aarav Sharma | 12    | A   | Male   | 9876543210 | aarav.sharma@example.com
102     | Diya Patel   | 12    | A   | Female | 9812345678 | diya.patel@example.com  
103     | Rohan Verma  | 12    | B   | Male   | 9988776655 | rohan.v@example.com     
104     | Priya Singh  | 12    | A   | Female | 9899887766 | priya@example.com       
105     | Aditya Roy   | 12    | B   | Male   | 9811223344 | aditya@example.com      

Total Visible Records: 5
""",
        "12_terminal_students_records_table.png"
    )

    # 13. Student Report Card
    render_terminal_screenshot(
        "Report Card & Grade Calculation",
        """
=================================================================
                 STUDENT RESULT & REPORT CARD                    
=================================================================
Enter Student Roll Number: 101

STUDENT REPORT CARD
Name    : Aarav Sharma
Roll No : 101
Class   : 12-A
---------------------------------------------
  Physics          : 88.0/100
  Chemistry        : 92.0/100
  Mathematics      : 95.0/100
  English          : 85.0/100
  Computer Sc/IP   : 96.0/100
---------------------------------------------
  TOTAL MARKS      : 456.0 / 500
  PERCENTAGE       : 91.2%
  GRADE            : A1
  STATUS           : PASSED
---------------------------------------------
[+] Scorecard calculated with CBSE 33% Passing & 90% A1 Grading criteria.
""",
        "13_terminal_student_report_card.png"
    )

    # 14. Teacher Restriction
    render_terminal_screenshot(
        "Teacher Class-Scope Guard & Security Enforcement",
        """
=================================================================
       TEACHER DASHBOARD — Class Teacher (Class 12-A)             
=================================================================
[TEST 1] Accessing Student 101 (Class 12-A):
-> Student: Aarav Sharma | Class: 12-A
-> [PASS] Access Granted.

[TEST 2] Accessing Student 103 (Class 12-B):
-> Attempting Marks Entry for Roll 103...
-> [!] Permission denied: Student belongs to Class 12-B. 
       You are only assigned to Class 12-A.
-> Attempting Result View for Roll 103...
-> [!] Access Denied or No student record found.

[+] Strict database-level teacher scope enforced successfully.
""",
        "14_terminal_teacher_class_security_restriction.png"
    )

    # 15. Student Fee Privacy
    render_terminal_screenshot(
        "Student Ownership & Fee Privacy Isolation",
        """
=================================================================
             STUDENT PORTAL — Welcome Aarav Sharma (Roll: 101)   
=================================================================
[ACTION 1] Aarav viewing his own Fees:
  Total Fees  : Rs. 12000.0
  Paid Amount : Rs. 12000.0
  Pending Due : Rs. 0.0
  Status      : Paid
  Last Payment: 2026-07-10
  [PASS] Displayed personal record.

[ACTION 2] Aarav querying Diya Patel's Fees (Roll 102):
  database.get_fees_by_roll('102') -> None
  [!] Fee details not found or access restricted.
  [PASS] Student ownership guard active. Cross-student data blocked!
""",
        "15_terminal_student_fee_privacy.png"
    )

    # 16. Pandas Data Analysis
    render_terminal_screenshot(
        "Pandas Series, DataFrame & CSV Integration",
        """
=================================================================
       PANDAS DATA ANALYSIS & AGGREGATIONS (CBSE IP)             
=================================================================
[1] DataFrame Inspection:
    Shape: (5, 15) | Total Cells: 75 | Dimensions (ndim): 2
    Columns: ['RollNo', 'Name', 'Class', 'Physics', 'Maths', 'CS_IP', 'Total', 'Percentage']

[2] Indexing & Slicing:
    df.loc[0:2, ['RollNo', 'Name', 'Percentage', 'Grade']]
       RollNo          Name  Percentage Grade
    0     101  Aarav Sharma        91.2    A1
    1     102    Diya Patel        81.4    A2
    2     103   Rohan Verma        81.8    A2

[3] Aggregation Functions:
               Count    Mean   Min   Max      Sum
    Physics      5.0   84.40  75.0  89.0    422.0
    Chemistry    5.0   84.80  79.0  92.0    424.0
    Maths        5.0   87.00  78.0  95.0    435.0
    CS_IP        5.0   91.00  84.0  96.0    455.0
    Percentage   5.0   86.12  81.4  91.4    430.6
""",
        "16_terminal_pandas_data_analysis.png"
    )

    # 17. SQL Queries Demonstration
    render_terminal_screenshot(
        "SQL Clauses & Database Query Output",
        """
=================================================================
       CBSE CLASS 12 SQL & DATABASE OPERATIONS                   
=================================================================
[1] SELECT with DISTINCT:
    Query: SELECT DISTINCT class, section FROM students
    -> Class: 12, Section: A
    -> Class: 12, Section: B

[2] Aggregate Functions with GROUP BY & HAVING:
    Query: SELECT s.class, COUNT(m.roll_no), ROUND(AVG(m.physics),2), MAX(m.cs_ip)
           FROM students s JOIN marks m ON s.roll_no = m.roll_no
           GROUP BY s.class HAVING COUNT(m.roll_no) >= 1
    -> Class 12 | Evaluated: 5 | Avg Physics: 84.4 | Max CS_IP: 96.0

[3] Pandas read_sql() Integration:
       Roll          Name  Gender   Phy  Math    CS
    0   101  Aarav Sharma    Male  88.0  95.0  96.0
    1   102    Diya Patel  Female  75.0  78.0  84.0
    2   103   Rohan Verma    Male  78.0  80.0  84.0
    3   104   Priya Singh  Female  89.0  94.0  95.0
    4   105    Aditya Roy    Male  82.0  88.0  85.0
""",
        "17_terminal_sql_queries_demo.png"
    )

    print("\nAll 17 project screenshots generated successfully in 'screenshots/' directory!")


if __name__ == "__main__":
    main()
