"""
main.py
-------
Student Management System — CBSE Class 12 Informatics Practices (IP) Project.
Complete Integration of:
1. Python + SQL Connectivity (database.py)
2. Pandas Data Analysis & CSV Transfer (data_analysis.py)
3. Matplotlib PyPlot Visualisation (charts.py)
4. Role-based Authentication with strict access control (ADMIN / TEACHER / STUDENT)
"""

import sys
import database
import charts
import data_analysis


# ── Utility Formatting Helpers ──────────────────────────────────────────────

def print_header(title):
    print("\n" + "=" * 65)
    print(f" {title.upper()} ".center(65, "="))
    print("=" * 65)


def print_table(headers, rows):
    if not rows:
        print("\n  [No records to display]\n")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print("\n" + header_line)
    print(sep_line)

    for row in rows:
        line = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
        print(line)
    print()


# ── 1. Student Management CRUD Operations ───────────────────────────────────

def handle_add_student():
    print_header("Add New Student")
    roll_no = input("Enter Roll Number       : ").strip()
    if not roll_no:
        print("[!] Roll Number cannot be empty.")
        return
    name = input("Enter Student Full Name : ").strip()
    if not name:
        print("[!] Student Name cannot be empty.")
        return
    cls = input("Enter Class (e.g., 11/12): ").strip() or "12"
    sec = input("Enter Section (e.g., A/B): ").strip().upper() or "A"
    dob = input("Enter DOB (YYYY-MM-DD)  : ").strip()
    gender = input("Enter Gender (Male/Female/Other): ").strip().capitalize() or "Male"
    phone = input("Enter Phone Number      : ").strip()
    email = input("Enter Email Address     : ").strip()

    data = {
        "roll_no": roll_no,
        "name": name,
        "class": cls,
        "section": sec,
        "dob": dob,
        "gender": gender,
        "phone": phone,
        "email": email
    }

    ok, msg = database.add_student(data)
    if ok:
        print(f"\n[+] Success: {msg}")
        data_analysis.export_db_to_csv()

        # ── Auto-generate student login account (password: firstname123) ──
        first_name = name.split()[0].lower()  # e.g. "jai" from "Jai Sharma"
        gen_password = f"{first_name}123"     # e.g. "jai123"
        gen_username = first_name

        ok2, msg2 = database.add_user(gen_username, gen_password, "STUDENT", name, roll_no, None, None)
        if ok2:
            print(f"[+] Student login account auto-created — Username: '{gen_username}'  Password: '{gen_password}'")
        else:
            # Username already taken — retry with roll number appended
            gen_username = f"{first_name}{roll_no}"
            ok3, msg3 = database.add_user(gen_username, gen_password, "STUDENT", name, roll_no, None, None)
            if ok3:
                print(f"[+] Student login account auto-created — Username: '{gen_username}'  Password: '{gen_password}'")
            else:
                print(f"[!] Student record saved, but login account could not be auto-created: {msg3}")
                print(f"    You may create one manually via User Account Administration (Option 9).")
    else:
        print(f"\n[!] Error: {msg}")


def handle_view_all_students():
    print_header("Student Records View")
    students = database.get_all_students()
    headers = ["Roll No", "Name", "Class", "Sec", "Gender", "Phone", "Email"]
    rows = [
        [s["roll_no"], s["name"], s["class"], s["section"], s["gender"], s["phone"], s["email"]]
        for s in students
    ]
    print_table(headers, rows)
    print(f"Total Visible Records: {len(students)}")


def handle_search_student():
    print_header("Search Student")
    print("1. Search by Name")
    print("2. Search by Roll Number")
    print("3. Search by Class")
    choice = input("Enter choice (1-3): ").strip()
    
    by_map = {"1": "Name", "2": "Roll Number", "3": "Class"}
    by = by_map.get(choice)
    if not by:
        print("[!] Invalid search criteria.")
        return

    query = input(f"Enter search query for {by}: ").strip()
    results = database.search_students(query, search_by=by)
    headers = ["Roll No", "Name", "Class", "Sec", "Gender", "Phone", "Email"]
    rows = [
        [s["roll_no"], s["name"], s["class"], s["section"], s["gender"], s["phone"], s["email"]]
        for s in results
    ]
    print_table(headers, rows)
    print(f"Found {len(results)} matching records.")


def handle_update_student():
    print_header("Update Student Details")
    roll_no = input("Enter Roll Number to update: ").strip()

    # Pre-check permission for current user
    if database.get_session()["role"] == "TEACHER":
        allowed, msg = database.check_teacher_scope(roll_no)
        if not allowed:
            print(f"\n[!] {msg}")
            return

    student = database.get_student_by_roll(roll_no)
    if not student:
        print(f"[!] No student found with Roll Number '{roll_no}'.")
        return

    print("\nLeave blank to keep existing value:")
    name = input(f"Name [{student['name']}]: ").strip() or student['name']
    cls = input(f"Class [{student['class']}]: ").strip() or student['class']
    sec = input(f"Section [{student['section']}]: ").strip() or student['section']
    dob = input(f"DOB [{student['dob']}]: ").strip() or student['dob']
    gender = input(f"Gender [{student['gender']}]: ").strip() or student['gender']
    phone = input(f"Phone [{student['phone']}]: ").strip() or student['phone']
    email = input(f"Email [{student['email']}]: ").strip() or student['email']

    updated = {
        "roll_no": roll_no,
        "name": name,
        "class": cls,
        "section": sec,
        "dob": dob,
        "gender": gender,
        "phone": phone,
        "email": email
    }

    ok, msg = database.update_student(roll_no, updated)
    if ok:
        print(f"\n[+] Success: {msg}")
        data_analysis.export_db_to_csv()
    else:
        print(f"\n[!] Error: {msg}")


def handle_delete_student():
    print_header("Delete Student")
    roll_no = input("Enter Roll Number to delete: ").strip()
    student = database.get_student_by_roll(roll_no)
    if not student:
        print(f"[!] No student found with Roll Number '{roll_no}'.")
        return

    confirm = input(f"Are you sure you want to delete {student['name']} ({roll_no})? (yes/no): ").strip().lower()
    if confirm in ["yes", "y"]:
        ok, msg = database.delete_student(roll_no)
        if ok:
            print(f"\n[+] Success: {msg}")
            data_analysis.export_db_to_csv()
        else:
            print(f"\n[!] Error: {msg}")
    else:
        print("[-] Operation cancelled.")


# ── 2. Marks & Academic Results ─────────────────────────────────────────────

def handle_marks_entry():
    print_header("Marks Entry")
    roll_no = input("Enter Student Roll Number: ").strip()

    # Pre-check permission for current user
    if database.get_session()["role"] == "TEACHER":
        allowed, msg = database.check_teacher_scope(roll_no)
        if not allowed:
            print(f"\n[!] {msg}")
            return

    student = database.get_student_by_roll(roll_no)
    if not student:
        print(f"[!] No student found with Roll Number '{roll_no}'.")
        return

    print(f"\nEntering Marks for: {student['name']} (Class {student['class']}-{student['section']})")
    current = database.get_marks(roll_no) or {}

    def get_valid_mark(subject, current_val):
        prompt = f"{subject} (0-100) [{current_val}]: " if current_val is not None else f"{subject} (0-100): "
        val_str = input(prompt).strip()
        if not val_str and current_val is not None:
            return current_val
        try:
            val = float(val_str)
            if 0 <= val <= 100:
                return val
            print("  [!] Mark must be between 0 and 100. Defaulted to 0.")
            return 0.0
        except ValueError:
            print("  [!] Invalid number. Defaulted to 0.")
            return 0.0

    p = get_valid_mark("Physics", current.get("physics"))
    c = get_valid_mark("Chemistry", current.get("chemistry"))
    m = get_valid_mark("Mathematics", current.get("maths"))
    e = get_valid_mark("English", current.get("english"))
    cs = get_valid_mark("Computer Science / IP", current.get("cs_ip"))

    marks_dict = {"physics": p, "chemistry": c, "maths": m, "english": e, "cs_ip": cs}
    ok, msg = database.save_marks(roll_no, marks_dict)
    if ok:
        print(f"\n[+] Success: {msg}")
        data_analysis.export_db_to_csv()
    else:
        print(f"\n[!] Error: {msg}")


def handle_view_result():
    print_header("Student Result & Report Card")
    roll_no = input("Enter Student Roll Number: ").strip()

    if database.get_session()["role"] == "TEACHER":
        allowed, msg = database.check_teacher_scope(roll_no)
        if not allowed:
            print(f"\n[!] {msg}")
            return

    res = database.get_result(roll_no)
    if not res:
        print(f"[!] Access Denied or No student record found for '{roll_no}'.")
        return

    student = res["student"]
    print(f"\nSTUDENT REPORT CARD")
    print(f"Name    : {student['name']}")
    print(f"Roll No : {student['roll_no']}")
    print(f"Class   : {student['class']}-{student['section']}")
    print("-" * 45)

    if not res.get("has_marks"):
        print("[!] Marks have not been entered for this student yet.")
        return

    marks = res["marks"]
    print(f"  Physics          : {marks.get('physics')}/100")
    print(f"  Chemistry        : {marks.get('chemistry')}/100")
    print(f"  Mathematics      : {marks.get('maths')}/100")
    print(f"  English          : {marks.get('english')}/100")
    print(f"  Computer Sc/IP   : {marks.get('cs_ip')}/100")
    print("-" * 45)
    print(f"  TOTAL MARKS      : {res['total']} / {res['max_total']}")
    print(f"  PERCENTAGE       : {res['percentage']}%")
    print(f"  GRADE            : {res['grade']}")
    print(f"  STATUS           : {res['status']}")
    print("-" * 45)

    plot_prompt = input("\nOpen Pyplot Visual Chart for this student? (y/n): ").strip().lower()
    if plot_prompt in ["y", "yes"]:
        charts.plot_student_marks(roll_no)


# ── 3. Fees Management ───────────────────────────────────────────────────────

def handle_fees_management():
    while True:
        print_header("Fees Management")
        print("1. View All Fees Records")
        print("2. Search Student Fees by Roll Number")
        print("3. Record / Update Fee Payment")
        print("4. Fees Status Overview Chart (Pyplot)")
        print("5. Back to Previous Menu")
        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            records = database.get_all_fees()
            headers = ["Roll No", "Student Name", "Class", "Total Fees", "Paid", "Pending", "Status"]
            rows = [
                [f["roll_no"], f.get("name", "N/A"), f"{f.get('class', '')}-{f.get('section', '')}", f"Rs.{f['total_fees']}", f"Rs.{f['paid']}", f"Rs.{f['pending']}", f["status"]]
                for f in records
            ]
            print_table(headers, rows)
        elif choice == "2":
            roll = input("Enter Roll Number: ").strip()
            f = database.get_fees_by_roll(roll)
            if not f:
                print(f"[!] No fee record found for '{roll}'.")
            else:
                print(f"\nFee details for {f.get('name', 'Student')} ({roll}):")
                print(f"Total Fees : Rs. {f['total_fees']}")
                print(f"Paid       : Rs. {f['paid']}")
                print(f"Pending    : Rs. {f['pending']}")
                print(f"Status     : {f['status']}")
                print(f"Last Paid  : {f['last_payment']}")
        elif choice == "3":
            roll = input("Enter Roll Number: ").strip()
            amount_str = input("Enter Payment Amount to add (Rs.): ").strip()
            try:
                amt = float(amount_str)
                ok, msg = database.update_fees(roll, amt)
                if ok:
                    print(f"\n[+] Success: {msg}")
                else:
                    print(f"\n[!] Error: {msg}")
            except ValueError:
                print("[!] Invalid amount entered. Must be a numeric value.")
        elif choice == "4":
            charts.plot_fees_distribution()
        elif choice == "5":
            break
        else:
            print("[!] Invalid option.")


# ── 4. User Account Management (Admin Exclusive) ────────────────────────────

def handle_user_management():
    while True:
        print_header("User Account Administration")
        print("1. View All Registered User Accounts")
        print("2. Create New User Account (Admin / Teacher / Student)")
        print("3. Delete User Account")
        print("4. Back to Admin Dashboard")
        ch = input("\nSelect User Option (1-4): ").strip()

        if ch == "1":
            users = database.get_all_users()
            headers = ["ID", "Username", "Role", "Display Name", "Linked Roll", "Class-Sec"]
            rows = [
                [u["id"], u["username"], u["role"], u["display_name"], u["linked_roll_no"] or "-", f"{u.get('assigned_class') or ''}-{u.get('assigned_section') or ''}".strip("-") or "-"]
                for u in users
            ]
            print_table(headers, rows)
            print(f"Total Registered Accounts: {len(users)}")

        elif ch == "2":
            uname = input("Enter Username       : ").strip()
            pwd = input("Enter Password       : ").strip()
            print("Select Role: 1. ADMIN  2. TEACHER  3. STUDENT")
            r_ch = input("Role choice (1-3)    : ").strip()
            role_map = {"1": "ADMIN", "2": "TEACHER", "3": "STUDENT"}
            role = role_map.get(r_ch, "STUDENT")
            dname = input("Enter Display Name   : ").strip()

            linked_roll = None
            assigned_cls = None
            assigned_sec = None

            if role == "STUDENT":
                linked_roll = input("Enter Linked Roll No : ").strip()
            elif role == "TEACHER":
                assigned_cls = input("Assigned Class (e.g. 12): ").strip()
                assigned_sec = input("Assigned Section (e.g. A): ").strip().upper()

            ok, msg = database.add_user(uname, pwd, role, dname, linked_roll, assigned_cls, assigned_sec)
            if ok:
                print(f"\n[+] Success: {msg}")
            else:
                print(f"\n[!] Error: {msg}")

        elif ch == "3":
            uname = input("Enter Username to Delete: ").strip()
            confirm = input(f"Confirm deleting account '{uname}'? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                ok, msg = database.delete_user(uname)
                if ok:
                    print(f"\n[+] Success: {msg}")
                else:
                    print(f"\n[!] Error: {msg}")
            else:
                print("[-] Deletion cancelled.")

        elif ch == "4":
            break
        else:
            print("[!] Invalid option.")


# ── 5. Pandas Data Analysis Hub (Class 12 IP Syllabus) ──────────────────────

def handle_pandas_data_analysis_menu():
    while True:
        print_header("Pandas Data Analysis & CSV Module (CBSE IP)")
        print("1. 📊 Series Creation, Attributes & Slicing Demo")
        print("2. 📋 DataFrame Attributes (shape, size, dtypes, head/tail)")
        print("3. 🎯 Indexing & Slicing with loc[] and iloc[]")
        print("4. 🔢 Statistical & Aggregate Functions (count, sum, mean, min, max, isnull)")
        print("5. 🔍 Filtering & Sorting DataFrame (Boolean Indexing, sort_values)")
        print("6. 🔁 DataFrame Iteration with iterrows()")
        print("7. 🛠️  DataFrame Manipulation (Add/Delete/Rename Columns & Update)")
        print("8. 💾 CSV Data Transfer (read_csv() / to_csv() sync)")
        print("9. ↩️  Back to Main Menu")

        ch = input("\nSelect Pandas Operation (1-9): ").strip()
        if ch == "1":
            data_analysis.demo_series_operations()
        elif ch == "2":
            data_analysis.show_dataframe_attributes()
        elif ch == "3":
            data_analysis.show_dataframe_indexing_slicing()
        elif ch == "4":
            data_analysis.show_summary_and_aggregations()
        elif ch == "5":
            data_analysis.show_filtering_and_sorting()
        elif ch == "6":
            data_analysis.show_dataframe_iteration()
        elif ch == "7":
            data_analysis.demo_df_manipulation()
        elif ch == "8":
            ok, msg = data_analysis.export_db_to_csv()
            print(f"\n[+] {msg}")
            df = data_analysis.load_dataframe_from_csv()
            print("\nPreview of CSV loaded via pd.read_csv():")
            print(df.head())
        elif ch == "9":
            break
        else:
            print("[!] Invalid option.")


# ── 6. Matplotlib PyPlot Visualisation Hub (All IP Chart Types) ──────────────

def handle_visual_analytics_menu():
    while True:
        print_header("Matplotlib PyPlot Data Visualisation (100% Real-Time)")
        print("1. 📊 Bar Chart: Individual Student Subject Marks")
        print("2. 📈 Line Chart: Student Subject Scores Profile vs Class Avg")
        print("3. 📊 Histogram: Class Marks Frequency Distribution")
        print("4. 💠 Scatter Plot: Physics vs Mathematics Score Correlation")
        print("5. 📦 Box Plot: Subject-Wise Marks Spread & Dispersion")
        print("6. 🥧 Pie Chart: Result Status (Pass/Compartment/Fail Breakdown)")
        print("7. 🏆 Horizontal Bar: Top Rankers Leaderboard")
        print("8. 🖼️  Multiple Subplots: Comprehensive 2x2 Analytics Dashboard")
        print("9. 💰 Pie Chart: Fees Payment Distribution")
        print("10. ↩️  Back to Main Menu")

        choice = input("\nSelect Visualization (1-10): ").strip()
        if choice == "1":
            roll = input("Enter Roll Number to plot: ").strip()
            charts.plot_student_marks(roll)
        elif choice == "2":
            roll = input("Enter Roll Number (default 101): ").strip() or "101"
            charts.plot_progress_line_chart(roll)
        elif choice == "3":
            charts.plot_marks_histogram()
        elif choice == "4":
            charts.plot_scatter_correlation()
        elif choice == "5":
            charts.plot_subject_boxplot()
        elif choice == "6":
            charts.plot_result_distribution()
        elif choice == "7":
            charts.plot_toppers(top_n=5)
        elif choice == "8":
            charts.plot_multiple_dashboard()
        elif choice == "9":
            charts.plot_fees_distribution()
        elif choice == "10":
            break
        else:
            print("[!] Invalid choice.")


# ── 7. Role-based Dashboards ────────────────────────────────────────────────

def admin_dashboard(user):
    while True:
        print_header(f"Admin Dashboard — Logged in as {user['display_name']}")
        print("1.  👨‍🎓 View All Students")
        print("2.  ➕ Add New Student")
        print("3.  🔍 Search Student")
        print("4.  ✏️  Update Student Record")
        print("5.  🗑️  Delete Student")
        print("6.  📊 Marks Entry")
        print("7.  📋 View Result / Report Card")
        print("8.  💰 Fees Management")
        print("9.  👥 User Account Administration (Create/Delete Accounts)")
        print("10. 🐼 Pandas Data Analysis (Class 12 IP Syllabus)")
        print("11. 📈 PyPlot Visualisation Hub (Line/Bar/Hist/Scatter/Box/Pie)")
        print("12. 🚪 Logout")
        
        choice = input("\nEnter choice (1-12): ").strip()
        if choice == "1":
            handle_view_all_students()
        elif choice == "2":
            handle_add_student()
        elif choice == "3":
            handle_search_student()
        elif choice == "4":
            handle_update_student()
        elif choice == "5":
            handle_delete_student()
        elif choice == "6":
            handle_marks_entry()
        elif choice == "7":
            handle_view_result()
        elif choice == "8":
            handle_fees_management()
        elif choice == "9":
            handle_user_management()
        elif choice == "10":
            handle_pandas_data_analysis_menu()
        elif choice == "11":
            handle_visual_analytics_menu()
        elif choice == "12":
            database.clear_session()
            print("\n[+] Logged out successfully.")
            break
        else:
            print("[!] Invalid selection. Please choose 1-12.")


def teacher_dashboard(user):
    assigned_cls = user.get("assigned_class", "12")
    assigned_sec = user.get("assigned_section", "A")
    while True:
        print_header(f"Teacher Dashboard — {user['display_name']} (Class {assigned_cls}-{assigned_sec})")
        print("1. 👨‍🎓 View Students in My Assigned Class")
        print("2. 🔍 Search Student (Scoped to My Class)")
        print("3. 📊 Enter / Update Marks (Scoped to My Class)")
        print("4. 📋 View Student Result (Scoped to My Class)")
        print("5. 🐼 Pandas Class Data Analysis")
        print("6. 📈 Matplotlib Visualizations")
        print("7. 🚪 Logout")

        choice = input("\nEnter choice (1-7): ").strip()
        if choice == "1":
            students = database.get_students_by_class(assigned_cls, assigned_sec)
            headers = ["Roll No", "Name", "Class", "Sec", "Gender", "Phone"]
            rows = [[s["roll_no"], s["name"], s["class"], s["section"], s["gender"], s["phone"]] for s in students]
            print_table(headers, rows)
            print(f"Total students in Class {assigned_cls}-{assigned_sec}: {len(students)}")
        elif choice == "2":
            handle_search_student()
        elif choice == "3":
            handle_marks_entry()
        elif choice == "4":
            handle_view_result()
        elif choice == "5":
            handle_pandas_data_analysis_menu()
        elif choice == "6":
            handle_visual_analytics_menu()
        elif choice == "7":
            database.clear_session()
            print("\n[+] Logged out successfully.")
            break
        else:
            print("[!] Invalid selection.")


def student_dashboard(user):
    roll_no = user.get("linked_roll_no")
    while True:
        print_header(f"Student Portal — Welcome {user['display_name']} (Roll: {roll_no})")
        print("1. 👤 View My Profile")
        print("2. 📋 View My Report Card / Results")
        print("3. 📊 View My Marks Chart (Pyplot)")
        print("4. 💰 View My Fees Status")
        print("5. 🚪 Logout")

        choice = input("\nEnter choice (1-5): ").strip()
        if choice == "1":
            s = database.get_student_by_roll(roll_no)
            if s:
                print(f"\nName     : {s['name']}")
                print(f"Roll No  : {s['roll_no']}")
                print(f"Class    : {s['class']}-{s['section']}")
                print(f"DOB      : {s['dob']}")
                print(f"Gender   : {s['gender']}")
                print(f"Phone    : {s['phone']}")
                print(f"Email    : {s['email']}")
            else:
                print("[!] Profile record not found.")
        elif choice == "2":
            res = database.get_result(roll_no)
            if res and res.get("has_marks"):
                marks = res["marks"]
                print("\n" + "=" * 40)
                print(f"STUDENT REPORT CARD - {user['display_name']}")
                print("=" * 40)
                print(f"Physics         : {marks.get('physics')}/100")
                print(f"Chemistry       : {marks.get('chemistry')}/100")
                print(f"Mathematics     : {marks.get('maths')}/100")
                print(f"English         : {marks.get('english')}/100")
                print(f"Computer Science: {marks.get('cs_ip')}/100")
                print("-" * 40)
                print(f"Total Marks     : {res['total']} / 500")
                print(f"Percentage      : {res['percentage']}%")
                print(f"Grade           : {res['grade']}")
                print(f"Final Status    : {res['status']}")
                print("=" * 40)
            else:
                print("\n[!] Results are not yet published.")
        elif choice == "3":
            charts.plot_student_marks(roll_no)
        elif choice == "4":
            f = database.get_fees_by_roll(roll_no)
            if f:
                print("\n" + "=" * 40)
                print(f"FEES STATUS - {user['display_name']}")
                print("=" * 40)
                print(f"Total Fees  : Rs. {f['total_fees']}")
                print(f"Paid Amount : Rs. {f['paid']}")
                print(f"Pending Due : Rs. {f['pending']}")
                print(f"Status      : {f['status']}")
                print(f"Last Payment: {f['last_payment']}")
                print("=" * 40)
            else:
                print("\n[!] Fee details not found or access restricted.")
        elif choice == "5":
            database.clear_session()
            print("\n[+] Logged out successfully.")
            break
        else:
            print("[!] Invalid selection.")


# ── Main Entry Point ─────────────────────────────────────────────────────────

def main():
    database.init_db()
    data_analysis.export_db_to_csv()

    while True:
        print_header("STUDENT MANAGEMENT SYSTEM (CBSE CLASS 12 IP)")
        print("1. Login to Account")
        print("2. Exit Application")
        
        choice = input("\nEnter choice (1-2): ").strip()
        if choice == "1":
            print("\n--- Login Screen ---")
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            user = database.verify_login(username, password)
            if user:
                role = user.get("role", "").upper()
                print(f"\n[+] Login successful as {role} ({user.get('display_name')})!")
                if role == "ADMIN":
                    admin_dashboard(user)
                elif role == "TEACHER":
                    teacher_dashboard(user)
                elif role == "STUDENT":
                    student_dashboard(user)
                else:
                    print(f"[!] Unknown role: {role}")
            else:
                print("\n[!] Invalid credentials. Check credentials list.")
        elif choice == "2":
            print("\nThank you for using Student Management System.")
            sys.exit(0)
        else:
            print("[!] Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
