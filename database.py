"""
database.py
-----------
SQLite-backed database layer for the Student Management System.
Handles all DB operations: auth, students, marks, results, fees.

Schema:
  users       (id, username, password, role, display_name, linked_roll_no)
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


# ── Connection helper ─────────────────────────────────────────────────────────
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ── DB Initialisation ─────────────────────────────────────────────────────────
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
            username         TEXT    UNIQUE NOT NULL,
            password         TEXT    NOT NULL,
            role             TEXT    NOT NULL CHECK(role IN ('ADMIN','TEACHER','STUDENT')),
            display_name     TEXT    NOT NULL,
            linked_roll_no   TEXT,
            assigned_class   TEXT,
            assigned_section TEXT
        )
    """)

    # students table
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            roll_no  TEXT PRIMARY KEY,
            name     TEXT NOT NULL,
            class    TEXT NOT NULL,
            section  TEXT NOT NULL,
            dob      TEXT,
            gender   TEXT,
            phone    TEXT,
            email    TEXT
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

    # ── Seed default accounts (only if users table is empty) ─────────
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        default_users = [
            # (username, password, role, display_name, linked_roll_no, assigned_class, assigned_section)
            ("admin",   "admin123",   "ADMIN",   "Admin",        None,  None, None),
            ("teacher", "teacher123", "TEACHER", "Class Teacher", None, "12", "A"),
            ("student", "student123", "STUDENT", "Test Student", "101", None, None),
        ]
        c.executemany("""
            INSERT INTO users
              (username, password, role, display_name,
               linked_roll_no, assigned_class, assigned_section)
            VALUES (?,?,?,?,?,?,?)
        """, default_users)

        # Seed sample students
        sample_students = [
            ("101", "Aarav Sharma", "12", "A", "2007-04-15", "Male",   "9876543210", "aarav.sharma@example.com"),
            ("102", "Diya Patel",   "12", "A", "2007-08-22", "Female", "9812345678", "diya.patel@example.com"),
            ("103", "Rohan Verma",  "12", "B", "2006-11-05", "Male",   "9988776655", "rohan.v@example.com"),
        ]
        c.executemany("""
            INSERT OR IGNORE INTO students
              (roll_no, name, class, section, dob, gender, phone, email)
            VALUES (?,?,?,?,?,?,?,?)
        """, sample_students)

        # Seed sample marks
        sample_marks = [
            ("101", 88, 92, 95, 85, 96),
            ("102", 75, 80, 78, 90, 84),
        ]
        c.executemany("""
            INSERT OR IGNORE INTO marks
              (roll_no, physics, chemistry, maths, english, cs_ip)
            VALUES (?,?,?,?,?,?)
        """, sample_marks)

        # Seed sample fees
        sample_fees = [
            ("101", 12000, 12000, 0,     "Paid",    "2026-07-10"),
            ("102", 12000, 6000,  6000,  "Partial", "2026-06-15"),
            ("103", 12000, 0,     12000, "Pending", "-"),
        ]
        c.executemany("""
            INSERT OR IGNORE INTO fees
              (roll_no, total_fees, paid, pending, status, last_payment)
            VALUES (?,?,?,?,?,?)
        """, sample_fees)

        conn.commit()

    conn.close()


# ── AUTH ──────────────────────────────────────────────────────────────────────
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


# ── ROLE GUARD ────────────────────────────────────────────────────────────────
def require_role(*allowed_roles):
    """
    Returns (True, "") if current session role is in allowed_roles.
    Returns (False, error_message) otherwise.
    Usage: ok, msg = require_role("ADMIN")
    """
    role = _session.get("role")
    if role in allowed_roles:
        return True, ""
    return False, f"Access denied. Required role: {' or '.join(allowed_roles)}. Your role: {role}"


# ── USER MANAGEMENT (ADMIN only) ──────────────────────────────────────────────
def get_all_users():
    ok, msg = require_role("ADMIN")
    if not ok:
        return []
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_user(username, password, role, display_name,
             linked_roll_no=None, assigned_class=None, assigned_section=None):
    ok, msg = require_role("ADMIN")
    if not ok:
        return False, msg
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
    conn = _get_conn()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True, f"User '{username}' deleted."


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
        conn.commit()
        conn.close()
        return True, f"Student {student_data.get('name')} added successfully!"
    except sqlite3.IntegrityError:
        return False, f"Student with Roll Number {roll} already exists."


def get_all_students():
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
    q = f"%{str(query).strip().lower()}%"
    conn = _get_conn()
    if search_by == "Roll Number":
        rows = conn.execute(
            "SELECT * FROM students WHERE LOWER(roll_no) LIKE ?", (q,)
        ).fetchall()
    elif search_by == "Class":
        rows = conn.execute(
            "SELECT * FROM students WHERE LOWER(class) LIKE ?", (q,)
        ).fetchall()
    else:  # Name (default)
        rows = conn.execute(
            "SELECT * FROM students WHERE LOWER(name) LIKE ?", (q,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_student(roll_no, updated_data):
    ok, msg = require_role("ADMIN", "TEACHER")
    if not ok:
        return False, msg

    roll_str = str(roll_no).strip()
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
    ok, msg = require_role("ADMIN", "TEACHER")
    if not ok:
        return False, msg

    roll_str = str(roll_no).strip()
    if not get_student_by_roll(roll_str):
        return False, f"Student with Roll Number {roll_str} does not exist."

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
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM marks WHERE roll_no=?", (str(roll_no).strip(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_result(roll_no):
    """STUDENT role can only access their own roll number."""
    roll_str = str(roll_no).strip()

    # Students can only view their own result
    if _session["role"] == "STUDENT":
        if _session["linked_roll_no"] != roll_str:
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
    ok, _ = require_role("ADMIN")
    if not ok:
        return []
    conn = _get_conn()
    rows = conn.execute("""
        SELECT f.*, s.name, s.class, s.section
        FROM fees f
        JOIN students s ON f.roll_no = s.roll_no
        ORDER BY f.roll_no
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_fees_by_roll(roll_no):
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM fees WHERE roll_no=?", (str(roll_no).strip(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_fees(roll_no, amount_paid):
    ok, msg = require_role("ADMIN")
    if not ok:
        return False, msg

    roll_str = str(roll_no).strip()
    existing = get_fees_by_roll(roll_str)
    today = datetime.date.today().strftime("%Y-%m-%d")

    conn = _get_conn()
    if existing:
        new_paid    = min(existing["paid"] + amount_paid, existing["total_fees"])
        new_pending = existing["total_fees"] - new_paid
        if new_pending == 0:    new_status = "Paid"
        elif new_paid == 0:     new_status = "Pending"
        else:                   new_status = "Partial"
        conn.execute("""
            UPDATE fees
            SET paid=?, pending=?, status=?, last_payment=?
            WHERE roll_no=?
        """, (new_paid, new_pending, new_status, today, roll_str))
        conn.commit()
        conn.close()
        return True, "Fees updated successfully."
    else:
        student = get_student_by_roll(roll_str)
        if not student:
            conn.close()
            return False, f"Student with Roll Number {roll_str} not found."
        paid    = min(amount_paid, 12000)
        pending = 12000 - paid
        status  = "Paid" if paid >= 12000 else ("Partial" if paid > 0 else "Pending")
        conn.execute("""
            INSERT INTO fees (roll_no, total_fees, paid, pending, status, last_payment)
            VALUES (?,?,?,?,?,?)
        """, (roll_str, 12000, paid, pending, status, today))
        conn.commit()
        conn.close()
        return True, "Fees record created and payment added."


# ── Bootstrap on import ───────────────────────────────────────────────────────
init_db()
