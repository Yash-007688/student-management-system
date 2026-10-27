"""
main.py
-------
Student Management System — Terminal / CLI Edition with Pyplot Visualizations.
Role-based access:
  - ADMIN: Full management (Students CRUD, Marks, Fees, Accounts, Analytics)
  - TEACHER: Class-specific Marks, Student Search/View, Analytics
  - STUDENT: View Personal Record, Results, Fees, and Graphical Performance
"""

import sys
import database
import charts

# ── Utility Helpers ──────────────────────────────────────────────────────────

def print_header(title):
    print("\n" + "=" * 65)
    print(f" {title.upper()} ".center(65, "="))
    print("=" * 65)

def print_table(headers, rows):
    if not rows:
        print("\n  [No records to display]\n")
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val)))

    # Print header row
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print("\n" + header_line)
    print(sep_line)

    for row in rows:
        line = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
        print(line)
    print()


# ── Student Management Operations ───────────────────────────────────────────

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
    else:
        print(f"\n[!] Error: {msg}")


def handle_view_all_students():
    print_header("All Registered Students")
    students = database.get_all_students()
    headers = ["Roll No", "Name", "Class", "Sec", "Gender", "Phone", "Email"]
    rows = [
        [s["roll_no"], s["name"], s["class"], s["section"], s["gender"], s["phone"], s["email"]]
        for s in students
    ]
    print_table(headers, rows)
    print(f"Total Students: {len(students)}")


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
        else:
            print(f"\n[!] Error: {msg}")
    else:
        print("[-] Operation cancelled.")


# ── Marks & Results Operations ──────────────────────────────────────────────

def handle_marks_entry():
    print_header("Marks Entry")
    roll_no = input("Enter Student Roll Number: ").strip()
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

    marks_dict = {
        "physics": p,
        "chemistry": c,
        "maths": m,
        "english": e,
        "cs_ip": cs
    }

    ok, msg = database.save_marks(roll_no, marks_dict)
    if ok:
        print(f"\n[+] Success: {msg}")
    else:
        print(f"\n[!] Error: {msg}")


def handle_view_result():
    print_header("Student Result & Report Card")
    roll_no = input("Enter Student Roll Number: ").strip()
    res = database.get_result(roll_no)
    if not res:
        print(f"[!] No student record found for '{roll_no}'.")
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

    plot_prompt = input("\nWould you like to open Pyplot Visual Chart for this student? (y/n): ").strip().lower()
    if plot_prompt in ["y", "yes"]:
        charts.plot_student_marks(roll_no)


# ── Fees Management ──────────────────────────────────────────────────────────

def handle_fees_management():
    while True:
        print_header("Fees Management")
        print("1. View All Fees Records")
        print("2. Search Student Fees by Roll Number")
        print("3. Record / Update Fee Payment")
        print("4. Fees Status Overview Chart (Pyplot)")
        print("5. Back to Main Menu")
        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            records = database.get_all_fees()
            headers = ["Roll No", "Student Name", "Class", "Total Fees", "Paid", "Pending", "Status"]
            rows = [
                [f["roll_no"], f["name"], f"{f['class']}-{f['section']}", f"Rs.{f['total_fees']}", f"Rs.{f['paid']}", f"Rs.{f['pending']}", f["status"]]
                for f in records
            ]
            print_table(headers, rows)

        elif choice == "2":
            roll = input("Enter Roll Number: ").strip()
            f = database.get_fees_by_roll(roll)
            if not f:
                print(f"[!] No fee record for '{roll}'.")
            else:
                print(f"\nFee details for {f['name']} ({roll}):")
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
                print("[!] Invalid amount entered.")

        elif choice == "4":
            charts.plot_fees_distribution()

        elif choice == "5":
            break
        else:
            print("[!] Invalid option.")


# ── Pyplot Visual Analytics Hub ──────────────────────────────────────────────

def handle_visual_analytics_menu():
    while True:
        print_header("Pyplot Visual Analytics & Charts")
        print("1. Individual Student Marks Bar Chart")
        print("2. Class Subject-wise Average Performance Chart")
        print("3. Top 5 Students Leaderboard (Horizontal Bar Chart)")
        print("4. Class Result Distribution (Pass / Compartment / Fail Pie Chart)")
        print("5. Fees Payment Distribution Chart")
        print("6. Back to Menu")
        choice = input("\nSelect Visualization (1-6): ").strip()

        if choice == "1":
            roll = input("Enter Roll Number to plot: ").strip()
            charts.plot_student_marks(roll)
        elif choice == "2":
            charts.plot_subject_averages()
        elif choice == "3":
            charts.plot_toppers(top_n=5)
        elif choice == "4":
            charts.plot_result_distribution()
        elif choice == "5":
            charts.plot_fees_distribution()
        elif choice == "6":
            break
        else:
            print("[!] Invalid choice.")


# ── Role-based Dashboards ───────────────────────────────────────────────────

def admin_dashboard(user):
    while True:
        print_header(f"Admin Dashboard — Logged in as {user['display_name']}")
        print("1. 👨‍🎓 View All Students")
        print("2. ➕ Add New Student")
        print("3. 🔍 Search Student")
        print("4. ✏️  Update Student Record")
        print("5. 🗑️  Delete Student")
        print("6. 📊 Marks Entry")
        print("7. 📋 View Result / Report Card")
        print("8. 💰 Fees Management")
        print("9. 📈 Pyplot Visual Analytics")
        print("10. 🚪 Logout")
        
        choice = input("\nEnter choice (1-10): ").strip()
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
            handle_visual_analytics_menu()
        elif choice == "10":
            database.clear_session()
            print("\n[+] Logged out successfully.")
            break
        else:
            print("[!] Invalid selection. Please choose 1-10.")


def teacher_dashboard(user):
    assigned_cls = user.get("assigned_class", "12")
    assigned_sec = user.get("assigned_section", "A")
    while True:
        print_header(f"Teacher Dashboard — {user['display_name']} (Class {assigned_cls}-{assigned_sec})")
        print("1. 👨‍🎓 View Students in My Class")
        print("2. 🔍 Search Student")
        print("3. 📊 Enter / Update Marks")
        print("4. 📋 View Student Result")
        print("5. 📈 Class Visual Analytics (Pyplot)")
        print("6. 🚪 Logout")

        choice = input("\nEnter choice (1-6): ").strip()
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
            handle_visual_analytics_menu()
        elif choice == "6":
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
                print("\n[!] Fee details not found.")

        elif choice == "5":
            database.clear_session()
            print("\n[+] Logged out successfully.")
            break
        else:
            print("[!] Invalid selection.")


# ── Main Entry Point ─────────────────────────────────────────────────────────

def main():
    database.init_db()

    while True:
        print_header("STUDENT MANAGEMENT SYSTEM (CBSE CLASS 12)")
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
                print("\n[!] Invalid username or password. Try demo: admin / admin123")
        elif choice == "2":
            print("\nThank you for using Student Management System. Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
