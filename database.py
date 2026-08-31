"""
database.py
-----------
Mock Database Interface Layer for Student Management System.
Supports roles: admin, teacher, student
"""

# ── Users ─────────────────────────────────────────────────────────────────────
# role: admin | teacher | student
# teacher has assigned_class + assigned_section
# student has roll_no linked to _SAMPLE_STUDENTS
_USERS = [
    {"username": "admin",    "password": "admin123",  "role": "admin",   "display_name": "Admin"},
    {"username": "teacher1", "password": "teach123",  "role": "teacher", "display_name": "Mrs. Kapoor",
     "assigned_class": "12", "assigned_section": "A"},
    {"username": "teacher2", "password": "teach456",  "role": "teacher", "display_name": "Mr. Singh",
     "assigned_class": "12", "assigned_section": "B"},
    {"username": "aarav",    "password": "student101", "role": "student", "display_name": "Aarav Sharma",
     "roll_no": "101"},
    {"username": "diya",     "password": "student102", "role": "student", "display_name": "Diya Patel",
     "roll_no": "102"},
    {"username": "rohan",    "password": "student103", "role": "student", "display_name": "Rohan Verma",
     "roll_no": "103"},
]

# ── Students ──────────────────────────────────────────────────────────────────
_SAMPLE_STUDENTS = [
    {"roll_no": "101", "name": "Aarav Sharma",  "class": "12", "section": "A",
     "dob": "2007-04-15", "gender": "Male",   "phone": "9876543210",
     "email": "aarav.sharma@example.com"},
    {"roll_no": "102", "name": "Diya Patel",    "class": "12", "section": "A",
     "dob": "2007-08-22", "gender": "Female", "phone": "9812345678",
     "email": "diya.patel@example.com"},
    {"roll_no": "103", "name": "Rohan Verma",   "class": "12", "section": "B",
     "dob": "2006-11-05", "gender": "Male",   "phone": "9988776655",
     "email": "rohan.v@example.com"},
]

# ── Marks ─────────────────────────────────────────────────────────────────────
_SAMPLE_MARKS = {
    "101": {"physics": 88, "chemistry": 92, "maths": 95, "english": 85, "cs_ip": 96},
    "102": {"physics": 75, "chemistry": 80, "maths": 78, "english": 90, "cs_ip": 84},
}

# ── Fees ──────────────────────────────────────────────────────────────────────
# status: Paid | Pending | Partial
_FEES = [
    {"roll_no": "101", "name": "Aarav Sharma",  "class": "12", "section": "A",
     "total_fees": 12000, "paid": 12000, "pending": 0,    "status": "Paid",
     "last_payment": "2026-07-10"},
    {"roll_no": "102", "name": "Diya Patel",    "class": "12", "section": "A",
     "total_fees": 12000, "paid": 6000,  "pending": 6000, "status": "Partial",
     "last_payment": "2026-06-15"},
    {"roll_no": "103", "name": "Rohan Verma",   "class": "12", "section": "B",
     "total_fees": 12000, "paid": 0,     "pending": 12000,"status": "Pending",
     "last_payment": "-"},
]


# ── Auth ──────────────────────────────────────────────────────────────────────
def verify_login(username, password):
    """
    Returns user dict if credentials match, else None.
    Dict has: username, role, display_name, and role-specific fields.
    """
    for u in _USERS:
        if u["username"] == username.strip() and u["password"] == password.strip():
            return dict(u)
    return None


def get_user_role(username):
    for u in _USERS:
        if u["username"] == username:
            return u.get("role", "student")
    return None


# ── Students CRUD ─────────────────────────────────────────────────────────────
def add_student(student_data):
    roll = str(student_data.get("roll_no", "")).strip()
    if not roll:
        return False, "Roll number cannot be empty."
    for s in _SAMPLE_STUDENTS:
        if s["roll_no"] == roll:
            return False, f"Student with Roll Number {roll} already exists."
    _SAMPLE_STUDENTS.append(student_data)
    return True, f"Student {student_data.get('name')} added successfully!"


def get_all_students():
    return list(_SAMPLE_STUDENTS)


def get_students_by_class(cls, section=None):
    """Returns students filtered by class and optionally section."""
    result = [s for s in _SAMPLE_STUDENTS if s["class"] == str(cls)]
    if section:
        result = [s for s in result if s["section"] == section]
    return result


def get_student_by_roll(roll_no):
    roll_str = str(roll_no).strip()
    for s in _SAMPLE_STUDENTS:
        if s["roll_no"] == roll_str:
            return dict(s)
    return None


def search_students(query, search_by="Name"):
    query_str = str(query).strip().lower()
    if not query_str:
        return get_all_students()
    results = []
    for s in _SAMPLE_STUDENTS:
        if search_by == "Roll Number" and query_str in s["roll_no"].lower():
            results.append(s)
        elif search_by == "Name" and query_str in s["name"].lower():
            results.append(s)
        elif search_by == "Class" and query_str in s["class"].lower():
            results.append(s)
    return results


def update_student(roll_no, updated_data):
    roll_str = str(roll_no).strip()
    for i, s in enumerate(_SAMPLE_STUDENTS):
        if s["roll_no"] == roll_str:
            _SAMPLE_STUDENTS[i] = updated_data
            return True, f"Student {roll_str} updated successfully."
    return False, f"Student with Roll Number {roll_str} not found."


def delete_student(roll_no):
    roll_str = str(roll_no).strip()
    for i, s in enumerate(_SAMPLE_STUDENTS):
        if s["roll_no"] == roll_str:
            del _SAMPLE_STUDENTS[i]
            if roll_str in _SAMPLE_MARKS:
                del _SAMPLE_MARKS[roll_str]
            return True, f"Student {roll_str} deleted successfully."
    return False, f"Student with Roll Number {roll_str} not found."


# ── Marks ─────────────────────────────────────────────────────────────────────
def save_marks(roll_no, marks_dict):
    roll_str = str(roll_no).strip()
    if not get_student_by_roll(roll_str):
        return False, f"Student with Roll Number {roll_str} does not exist."
    _SAMPLE_MARKS[roll_str] = marks_dict
    return True, f"Marks saved for Roll Number {roll_str}."


def get_marks(roll_no):
    return _SAMPLE_MARKS.get(str(roll_no).strip(), None)


def get_result(roll_no):
    roll_str = str(roll_no).strip()
    student = get_student_by_roll(roll_str)
    if not student:
        return None
    marks = get_marks(roll_str)
    if not marks:
        return {"student": student, "has_marks": False,
                "message": "Marks not entered yet."}

    p  = marks.get("physics", 0)
    c  = marks.get("chemistry", 0)
    m  = marks.get("maths", 0)
    e  = marks.get("english", 0)
    cs = marks.get("cs_ip", 0)
    total = p + c + m + e + cs
    percentage = round(total / 5.0, 2)

    if percentage >= 90:   grade = "A1"
    elif percentage >= 80: grade = "A2"
    elif percentage >= 70: grade = "B1"
    elif percentage >= 60: grade = "B2"
    elif percentage >= 50: grade = "C1"
    elif percentage >= 40: grade = "C2"
    elif percentage >= 33: grade = "D"
    else:                  grade = "E (Needs Improvement)"

    failed = [sub for sub, score in {
        "Physics": p, "Chemistry": c, "Mathematics": m,
        "English": e, "Computer Science / IP": cs
    }.items() if score < 33]

    if   len(failed) == 0: status = "PASSED"
    elif len(failed) <= 2: status = f"COMPARTMENT ({', '.join(failed)})"
    else:                  status = "FAILED"

    return {"student": student, "has_marks": True, "marks": marks,
            "total": total, "max_total": 500, "percentage": percentage,
            "grade": grade, "status": status, "failed_subjects": failed}


# ── Fees ──────────────────────────────────────────────────────────────────────
def get_all_fees():
    return list(_FEES)


def get_fees_by_roll(roll_no):
    roll_str = str(roll_no).strip()
    for f in _FEES:
        if f["roll_no"] == roll_str:
            return dict(f)
    return None


def update_fees(roll_no, amount_paid):
    """Add a payment to a student's fees record."""
    roll_str = str(roll_no).strip()
    for f in _FEES:
        if f["roll_no"] == roll_str:
            f["paid"]    = min(f["paid"] + amount_paid, f["total_fees"])
            f["pending"] = f["total_fees"] - f["paid"]
            if f["pending"] == 0:
                f["status"] = "Paid"
            elif f["paid"] == 0:
                f["status"] = "Pending"
            else:
                f["status"] = "Partial"
            import datetime
            f["last_payment"] = datetime.date.today().strftime("%Y-%m-%d")
            return True, "Fees updated successfully."
    # Student exists but no fees record yet — create one
    student = get_student_by_roll(roll_str)
    if student:
        paid = min(amount_paid, 12000)
        _FEES.append({
            "roll_no": roll_str, "name": student["name"],
            "class": student["class"], "section": student["section"],
            "total_fees": 12000, "paid": paid,
            "pending": 12000 - paid,
            "status": "Paid" if paid >= 12000 else ("Partial" if paid > 0 else "Pending"),
            "last_payment": __import__("datetime").date.today().strftime("%Y-%m-%d")
        })
        return True, "Fees record created and payment added."
    return False, f"Student with Roll Number {roll_str} not found."
