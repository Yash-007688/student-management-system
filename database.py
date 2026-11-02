"""
database.py
-----------
SQLite-backed database layer for the Student Management System.
Handles all DB operations: auth, students, marks, results, fees.

Schema:
  users       (id, username, password, role, display_name, linked_roll_no, assigned_class, assigned_section)
  students    (roll_no, name, class, section, dob, gender, phone, email)
  marks       (roll_no, physics, chemistry, maths, english, cs_ip)
  fees        (roll_no, total_fees, paid, pending, status, last_payment)

Roles: ADMIN | TEACHER | STUDENT
"""

import sqlite3
import os
import datetime

# ── DB path ───────────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(_BASE_DIR, "school.db")

# ── Session (in-memory, current logged-in user) ───────────────────────────────
_session = {
    "username":       None,
    "role":           None,   # ADMIN | TEACHER | STUDENT
    "display_name":   None,
    "linked_roll_no": None,   # for STUDENT accounts
    "assigned_class": None,   # for TEACHER accounts
    "assigned_section": None,
}


def get_session():
    """Returns a copy of the current session dict."""
    return dict(_session)


def _set_session(user_row):
    """Populate session from a users table row (sqlite3.Row)."""
    _session["username"]         = user_row["username"]
    _session["role"]             = user_row["role"]
    _session["display_name"]     = user_row["display_name"]
    _session["linked_roll_no"]   = user_row["linked_roll_no"]
    _session["assigned_class"]   = user_row["assigned_class"]
    _session["assigned_section"] = user_row["assigned_section"]


def clear_session():
    for k in _session:
        _session[k] = None


# ── Connection helper ────────────────────────────────────────────────────────
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── DB Initialisation ────────────────────────────────────────────────────────
def init_db():
    """
    Creates all tables if they don't exist and seeds default accounts.
    Safe to call on every startup.
    """
    conn = _get_conn()
    c = conn.cursor()

    # users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            username         TEXT UNIQUE NOT NULL,
            password         TEXT NOT NULL,
            role             TEXT NOT NULL,
            display_name     TEXT,
            linked_roll_no   TEXT,
            assigned_class   TEXT,
            assigned_section TEXT
        )
    """)

    # students table
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll_no TEXT PRIMARY KEY,
            name    TEXT NOT NULL,
            class   TEXT NOT NULL,
            section TEXT NOT NULL,
            dob     TEXT,
            gender  TEXT,
            phone   TEXT,
            email   TEXT
        )
    """)

    # marks table
    c.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            roll_no   TEXT PRIMARY KEY,
            physics   REAL DEFAULT 0,
            chemistry REAL DEFAULT 0,
            maths     REAL DEFAULT 0,
            english   REAL DEFAULT 0,
            cs_ip     REAL DEFAULT 0,
            FOREIGN KEY (roll_no) REFERENCES students(roll_no)
        )
    """)

    # fees table
    c.execute("""
        CREATE TABLE IF NOT EXISTS fees (
            roll_no      TEXT PRIMARY KEY,
            total_fees   REAL DEFAULT 12000,
            paid         REAL DEFAULT 0,
            pending      REAL DEFAULT 12000,
            status       TEXT DEFAULT 'Pending',
            last_payment TEXT DEFAULT '-',
            FOREIGN KEY (roll_no) REFERENCES students(roll_no)
        )
    """)

    conn.commit()

    # ── Seed standard accounts if missing ────────────────────────────────────
    default_users = [
        ("admin",   "admin123",   "ADMIN",   "Admin",         None,  None, None),
        ("teacher", "teacher123", "TEACHER", "Class Teacher",  None,  "12", "A"),
        ("aarav",   "aarav123",   "STUDENT", "Aarav Sharma",   "101", None, None),
        ("diya",    "diya123",    "STUDENT", "Diya Patel",     "102", None, None),
        ("rohan",   "rohan123",   "STUDENT", "Rohan Verma",    "103", None, None),
        ("priya",   "priya123",   "STUDENT", "Priya Singh",    "104", None, None),
        ("aditya",  "aditya12",   "STUDENT", "Aditya Roy",     "105", None, None),
    ]
    for u in default_users:
        c.execute("""
            INSERT INTO users (username, password, role, display_name, linked_roll_no, assigned_class, assigned_section)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password=excluded.password,
                display_name=excluded.display_name,
                linked_roll_no=excluded.linked_roll_no,
                assigned_class=excluded.assigned_class,
                assigned_section=excluded.assigned_section
        """, u)

    # Seed sample students if missing
    sample_students = [
        ("101", "Aarav Sharma", "12", "A", "2007-04-15", "Male",   "9876543210", "aarav.sharma@example.com"),
        ("102", "Diya Patel",   "12", "A", "2007-08-22", "Female", "9812345678", "diya.patel@example.com"),
        ("103", "Rohan Verma",  "12", "B", "2006-11-05", "Male",   "9988776655", "rohan.v@example.com"),
        ("104", "Priya Singh",  "12", "A", "2007-01-10", "Female", "9899887766", "priya@example.com"),
        ("105", "Aditya Roy",   "12", "B", "2006-09-12", "Male",   "9811223344", "aditya@example.com"),
    ]
    for s in sample_students:
        c.execute("""
            INSERT OR IGNORE INTO students (roll_no, name, class, section, dob, gender, phone, email)
            VALUES (?,?,?,?,?,?,?,?)
        """, s)

    # Seed sample marks
    sample_marks = [
        ("101", 88, 92, 95, 85, 96),
        ("102", 75, 80, 78, 90, 84),
        ("103", 78, 82, 80, 85, 84),
        ("104", 89, 91, 94, 88, 95),
        ("105", 82, 79, 88, 90, 85),
    ]
    for m in sample_marks:
        c.execute("""
            INSERT OR IGNORE INTO marks (roll_no, physics, chemistry, maths, english, cs_ip)
            VALUES (?,?,?,?,?,?)
        """, m)

    # Seed sample fees
    sample_fees = [
        ("101", 12000, 12000, 0,     "Paid",    "2026-07-10"),
        ("102", 12000, 6000,  6000,  "Partial", "2026-06-15"),
        ("103", 12000, 0,     12000, "Pending", "-"),
        ("104", 12000, 5000,  7000,  "Partial", "2026-08-20"),
        ("105", 12000, 8000,  4000,  "Partial", "2026-09-05"),
    ]
    for f in sample_fees:
        c.execute("""
            INSERT OR IGNORE INTO fees (roll_no, total_fees, paid, pending, status, last_payment)
            VALUES (?,?,?,?,?,?)
        """, f)

    conn.commit()
    conn.close()


# ── AUTH & PERMISSIONS ────────────────────────────────────────────────────────
def verify_login(username, password):
    """
    Authenticates user against SQLite users table.
    Returns user dict on success, None on failure.
    Automatically sets the session.
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM users
        WHERE username = ? AND password = ?
    """, (username.strip(), password.strip()))
    row = c.fetchone()
    conn.close()

    if row:
        _set_session(row)
        return dict(row)
    return None


def require_role(*allowed_roles):
    """Guard: returns (True, '') if current session role is allowed."""
    cur = _session.get("role")
    if cur in allowed_roles:
        return True, ""
    return False, f"Access denied. Requires one of: {', '.join(allowed_roles)}."


def check_teacher_scope(student_or_roll):
    """
    Validates whether the current teacher session has permission for this student.
    Teachers can ONLY access students in their assigned_class and assigned_section.
    Admins have universal access.
    """
    if _session["role"] == "ADMIN":
        return True, ""
    if _session["role"] != "TEACHER":
        return False, "Access denied. Action restricted to teachers or admin."

    t_cls = str(_session.get("assigned_class", "")).strip()
    t_sec = str(_session.get("assigned_section", "")).strip()

    if isinstance(student_or_roll, dict):
        s_cls = str(student_or_roll.get("class", "")).strip()
        s_sec = str(student_or_roll.get("section", "")).strip()
    else:
        s = get_student_by_roll(str(student_or_roll).strip())
        if not s:
            return False, f"Student with Roll Number {student_or_roll} does not exist."
        s_cls = str(s.get("class", "")).strip()
        s_sec = str(s.get("section", "")).strip()

    if s_cls == t_cls and s_sec == t_sec:
        return True, ""
    return False, f"Permission denied: Student belongs to Class {s_cls}-{s_sec}. You are only assigned to Class {t_cls}-{t_sec}."


# ── USER MANAGEMENT ───────────────────────────────────────────────────────────
def get_all_users():
    ok, msg = require_role("ADMIN")
    if not ok:
        return []
    conn = _get_conn()
    rows = conn.execute("SELECT id, username, role, display_name, linked_roll_no, assigned_class, assigned_section FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_user(username, password, role, display_name, linked_roll_no=None, assigned_class=None, assigned_section=None):
    ok, msg = require_role("ADMIN")
    if not ok:
        return False, msg

    username = username.strip()
    password = password.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."

    try:
        conn = _get_conn()
        conn.execute("""
            INSERT INTO users
              (username, password, role, display_name,
               linked_roll_no, assigned_class, assigned_section)
            VALUES (?,?,?,?,?,?,?)
        """, (username, password, role.upper(), display_name,
              linked_roll_no, assigned_class, assigned_section))
        conn.commit()
        conn.close()
        return True, f"User '{username}' created successfully."
    except sqlite3.IntegrityError:
        return False, f"Username '{username}' already exists."


def delete_user(username):
    ok, msg = require_role("ADMIN")
    if not ok:
        return False, msg
    if username.strip().lower() == "admin":
        return False, "The master 'admin' account cannot be deleted."

    conn = _get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username.strip(),))
    conn.commit()
    affected = c.rowcount
    conn.close()
    if affected:
        return True, f"User '{username}' deleted successfully."
    return False, f"User '{username}' not found."


# ── STUDENTS CRUD ─────────────────────────────────────────────────────────────
def add_student(student_data):
    ok, msg = require_role("ADMIN")
    if not ok:
        return False, msg

    roll = str(student_data.get("roll_no", "")).strip()
    if not roll:
        return False, "Roll number cannot be empty."

    try:
        conn = _get_conn()
        conn.execute("""
            INSERT INTO students
              (roll_no, name, class, section, dob, gender, phone, email)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            roll,
            student_data.get("name", ""),
            student_data.get("class", ""),
            student_data.get("section", ""),
            student_data.get("dob", ""),
            student_data.get("gender", ""),
            student_data.get("phone", ""),
            student_data.get("email", ""),
        ))
        # Initialize default pending fee record
        conn.execute("""
            INSERT OR IGNORE INTO fees (roll_no, total_fees, paid, pending, status, last_payment)
            VALUES (?, 12000, 0, 12000, 'Pending', '-')
        """, (roll,))
        conn.commit()
        conn.close()
        return True, f"Student {student_data.get('name')} added successfully!"
    except sqlite3.IntegrityError:
        return False, f"Student with Roll Number {roll} already exists."


def get_all_students():
    """
    Returns student list scoped by user role.
    Teachers receive only their assigned class/section.
    """
    if _session["role"] == "TEACHER":
        t_cls = _session.get("assigned_class", "12")
        t_sec = _session.get("assigned_section", "A")
        return get_students_by_class(t_cls, t_sec)

    conn = _get_conn()
    rows = conn.execute("SELECT * FROM students ORDER BY roll_no").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_students_by_class(cls, section=None):
    conn = _get_conn()
    if section:
        rows = conn.execute(
            "SELECT * FROM students WHERE class=? AND section=? ORDER BY roll_no",
            (str(cls), section)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM students WHERE class=? ORDER BY roll_no",
            (str(cls),)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_by_roll(roll_no):
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM students WHERE roll_no=?", (str(roll_no).strip(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def search_students(query, search_by="Name"):
    """
    Searches students.
    Enforces strict teacher scope: Teachers can only view search results from their assigned class/section.
    """
    q = f"%{str(query).strip().lower()}%"
    conn = _get_conn()
    if search_by == "Roll Number":
        rows = conn.execute("SELECT * FROM students WHERE LOWER(roll_no) LIKE ?", (q,)).fetchall()
    elif search_by == "Class":
        rows = conn.execute("SELECT * FROM students WHERE LOWER(class) LIKE ?", (q,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM students WHERE LOWER(name) LIKE ?", (q,)).fetchall()
    conn.close()

    results = [dict(r) for r in rows]
    if _session["role"] == "TEACHER":
        t_cls = str(_session.get("assigned_class", "")).strip()
        t_sec = str(_session.get("assigned_section", "")).strip()
        results = [s for s in results if str(s.get("class")).strip() == t_cls and str(s.get("section")).strip() == t_sec]

    return results


def update_student(roll_no, updated_data):
    ok, msg = require_role("ADMIN", "TEACHER")
    if not ok:
        return False, msg

    roll_str = str(roll_no).strip()
    # Check teacher boundary
    allowed, guard_msg = check_teacher_scope(roll_str)
    if not allowed:
        return False, guard_msg

    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE students
        SET name=?, class=?, section=?, dob=?, gender=?, phone=?, email=?
        WHERE roll_no=?
    """, (
        updated_data.get("name", ""),
        updated_data.get("class", ""),
        updated_data.get("section", ""),
        updated_data.get("dob", ""),
        updated_data.get("gender", ""),
        updated_data.get("phone", ""),
        updated_data.get("email", ""),
        roll_str,
    ))
    conn.commit()
    affected = c.rowcount
    conn.close()
    if affected:
        return True, f"Student {roll_str} updated successfully."
    return False, f"Student with Roll Number {roll_str} not found."


def delete_student(roll_no):
    ok, msg = require_role("ADMIN")
    if not ok:
        return False, msg

    roll_str = str(roll_no).strip()
    conn = _get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM marks WHERE roll_no=?", (roll_str,))
    c.execute("DELETE FROM fees  WHERE roll_no=?", (roll_str,))
    c.execute("DELETE FROM students WHERE roll_no=?", (roll_str,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    if affected:
        return True, f"Student {roll_str} deleted successfully."
    return False, f"Student with Roll Number {roll_str} not found."


# ── MARKS ─────────────────────────────────────────────────────────────────────
def save_marks(roll_no, marks_dict):
    """
    Saves student marks.
    Enforces teacher scope: A teacher cannot enter/edit marks for students of other classes.
    """
    ok, msg = require_role("ADMIN", "TEACHER")
    if not ok:
        return False, msg

    roll_str = str(roll_no).strip()
    allowed, guard_msg = check_teacher_scope(roll_str)
    if not allowed:
        return False, guard_msg

    conn = _get_conn()
    conn.execute("""
        INSERT INTO marks (roll_no, physics, chemistry, maths, english, cs_ip)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(roll_no) DO UPDATE SET
            physics=excluded.physics,
            chemistry=excluded.chemistry,
            maths=excluded.maths,
            english=excluded.english,
            cs_ip=excluded.cs_ip
    """, (
        roll_str,
        marks_dict.get("physics", 0),
        marks_dict.get("chemistry", 0),
        marks_dict.get("maths", 0),
        marks_dict.get("english", 0),
        marks_dict.get("cs_ip", 0),
    ))
    conn.commit()
    conn.close()
    return True, f"Marks saved for Roll Number {roll_str}."


def get_marks(roll_no):
    roll_str = str(roll_no).strip()
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM marks WHERE roll_no=?", (roll_str,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_result(roll_no):
    """
    Calculates student report card.
    Strict privacy & scope enforcement:
    - STUDENT: Can ONLY view their own linked roll number result.
    - TEACHER: Can ONLY view results of students in their assigned class/section.
    - ADMIN: Unrestricted access.
    """
    roll_str = str(roll_no).strip()

    if _session["role"] == "STUDENT":
        if _session["linked_roll_no"] != roll_str:
            return None

    if _session["role"] == "TEACHER":
        allowed, _ = check_teacher_scope(roll_str)
        if not allowed:
            return None

    student = get_student_by_roll(roll_str)
    if not student:
        return None

    marks = get_marks(roll_str)
    if not marks:
        return {"student": student, "has_marks": False,
                "message": "Marks not entered yet."}

    p  = marks.get("physics",   0)
    c  = marks.get("chemistry", 0)
    m  = marks.get("maths",     0)
    e  = marks.get("english",   0)
    cs = marks.get("cs_ip",     0)
    total      = p + c + m + e + cs
    percentage = round(total / 5.0, 2)

    if   percentage >= 90: grade = "A1"
    elif percentage >= 80: grade = "A2"
    elif percentage >= 70: grade = "B1"
    elif percentage >= 60: grade = "B2"
    elif percentage >= 50: grade = "C1"
    elif percentage >= 40: grade = "C2"
    elif percentage >= 33: grade = "D"
    else:                  grade = "E (Needs Improvement)"

    subject_map = {
        "Physics": p, "Chemistry": c, "Mathematics": m,
        "English": e, "Computer Science / IP": cs
    }
    failed = [sub for sub, score in subject_map.items() if score < 33]

    if   len(failed) == 0: status = "PASSED"
    elif len(failed) <= 2: status = f"COMPARTMENT ({', '.join(failed)})"
    else:                  status = "FAILED"

    return {
        "student": student, "has_marks": True, "marks": dict(marks),
        "total": total, "max_total": 500, "percentage": percentage,
        "grade": grade, "status": status, "failed_subjects": failed,
    }


# ── FEES ──────────────────────────────────────────────────────────────────────
def get_all_fees():
    """
    Returns fees records. Accessible to ADMIN and system analytical modules.
    STUDENT accounts cannot access all fees.
    """
    if _session["role"] == "STUDENT":
        return []
    conn = _get_conn()
    rows = conn.execute("""
        SELECT f.*, s.name, s.class, s.section
        FROM fees f
        LEFT JOIN students s ON f.roll_no = s.roll_no
        ORDER BY f.roll_no
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_fees_by_roll(roll_no):
    """
    Returns student fee record.
    Security Guard:
    - If current session is STUDENT, they can ONLY view their own fee record.
    - Any attempt by student to query another roll_no returns None.
    """
    roll_str = str(roll_no).strip()

    if _session["role"] == "STUDENT":
        if _session.get("linked_roll_no") != roll_str:
            return None

    conn = _get_conn()
    row = conn.execute("""
        SELECT f.*, s.name, s.class, s.section
        FROM fees f
        LEFT JOIN students s ON f.roll_no = s.roll_no
        WHERE f.roll_no=?
    """, (roll_str,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_fees(roll_no, amount_paid):
    """
    Records fee payment.
    Enforces positive payment validation (> 0).
    """
    ok, msg = require_role("ADMIN")
    if not ok:
        return False, msg

    try:
        amount_paid = float(amount_paid)
    except (ValueError, TypeError):
        return False, "Invalid payment amount. Must be a valid number."

    if amount_paid <= 0:
        return False, "Invalid payment amount: Payment must be strictly greater than 0."

    roll_str = str(roll_no).strip()
    existing = get_fees_by_roll(roll_str)
    today = datetime.date.today().strftime("%Y-%m-%d")

    conn = _get_conn()
    if existing:
        if existing["pending"] <= 0:
            conn.close()
            return False, f"Fees for Roll Number {roll_str} are already fully paid."

        new_paid    = min(existing["paid"] + amount_paid, existing["total_fees"])
        new_pending = max(0.0, existing["total_fees"] - new_paid)
        new_status  = "Paid" if new_pending == 0 else "Partial"

        conn.execute("""
            UPDATE fees
            SET paid=?, pending=?, status=?, last_payment=?
            WHERE roll_no=?
        """, (new_paid, new_pending, new_status, today, roll_str))
        conn.commit()
        conn.close()
        return True, f"Payment of Rs. {amount_paid} recorded. Remaining Due: Rs. {new_pending}."
    else:
        student = get_student_by_roll(roll_str)
        if not student:
            conn.close()
            return False, f"Student with Roll Number {roll_str} not found."
        paid    = min(amount_paid, 12000.0)
        pending = max(0.0, 12000.0 - paid)
        status  = "Paid" if pending == 0 else ("Partial" if paid > 0 else "Pending")
        conn.execute("""
            INSERT INTO fees (roll_no, total_fees, paid, pending, status, last_payment)
            VALUES (?,?,?,?,?,?)
        """, (roll_str, 12000.0, paid, pending, status, today))
        conn.commit()
        conn.close()
        return True, f"Fees record created. Payment of Rs. {paid} added."


# ── Bootstrap on import ───────────────────────────────────────────────────────
init_db()
