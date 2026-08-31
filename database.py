"""
database.py
-----------
Stub / Mock Database Interface Layer for Student Management System.
The actual SQLite implementation will be provided by the backend partner.
This module maintains standard function signatures and mock in-memory data
so the UI can run, add, update, delete, view, and test results immediately.
"""

# Sample in-memory store for initial testing until real database is attached
_SAMPLE_STUDENTS = [
    {
        "roll_no": "101",
        "name": "Aarav Sharma",
        "class": "12",
        "section": "A",
        "dob": "2007-04-15",
        "gender": "Male",
        "phone": "9876543210",
        "email": "aarav.sharma@example.com"
    },
    {
        "roll_no": "102",
        "name": "Diya Patel",
        "class": "12",
        "section": "A",
        "dob": "2007-08-22",
        "gender": "Female",
        "phone": "9812345678",
        "email": "diya.patel@example.com"
    },
    {
        "roll_no": "103",
        "name": "Rohan Verma",
        "class": "12",
        "section": "B",
        "dob": "2006-11-05",
        "gender": "Male",
        "phone": "9988776655",
        "email": "rohan.v@example.com"
    }
]

_SAMPLE_MARKS = {
    "101": {"physics": 88, "chemistry": 92, "maths": 95, "english": 85, "cs_ip": 96},
    "102": {"physics": 75, "chemistry": 80, "maths": 78, "english": 90, "cs_ip": 84}
}


def verify_login(username, password):
    """
    Validates user login credentials.
    Default teacher/admin login: admin / admin123
    """
    # Simple default credentials for Class 12 project demo
    return username.strip() == "admin" and password.strip() == "admin123"


def add_student(student_data):
    """
    Adds a new student record.
    student_data is a dict containing:
    roll_no, name, class, section, dob, gender, phone, email
    Returns (success: bool, message: str)
    """
    roll = str(student_data.get("roll_no", "")).strip()
    if not roll:
        return False, "Roll number cannot be empty."

    # Check if roll number already exists
    for s in _SAMPLE_STUDENTS:
        if s["roll_no"] == roll:
            return False, f"Student with Roll Number {roll} already exists."

    _SAMPLE_STUDENTS.append(student_data)
    return True, f"Student {student_data.get('name')} added successfully!"


def get_all_students():
    """
    Returns a list of all student dictionaries.
    """
    return list(_SAMPLE_STUDENTS)


def get_student_by_roll(roll_no):
    """
    Fetches a single student dictionary by Roll Number.
    Returns dict or None.
    """
    roll_str = str(roll_no).strip()
    for s in _SAMPLE_STUDENTS:
        if s["roll_no"] == roll_str:
            return dict(s)
    return None


def search_students(query, search_by="Name"):
    """
    Searches students by 'Roll Number' or 'Name'.
    Returns matching list of student dictionaries.
    """
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
    """
    Updates an existing student's record by Roll Number.
    Returns (success: bool, message: str)
    """
    roll_str = str(roll_no).strip()
    for i, s in enumerate(_SAMPLE_STUDENTS):
        if s["roll_no"] == roll_str:
            _SAMPLE_STUDENTS[i] = updated_data
            return True, f"Student {roll_str} updated successfully."
    return False, f"Student with Roll Number {roll_str} not found."


def delete_student(roll_no):
    """
    Deletes a student record by Roll Number.
    Returns (success: bool, message: str)
    """
    roll_str = str(roll_no).strip()
    for i, s in enumerate(_SAMPLE_STUDENTS):
        if s["roll_no"] == roll_str:
            del _SAMPLE_STUDENTS[i]
            if roll_str in _SAMPLE_MARKS:
                del _SAMPLE_MARKS[roll_str]
            return True, f"Student {roll_str} deleted successfully."
    return False, f"Student with Roll Number {roll_str} not found."


def save_marks(roll_no, marks_dict):
    """
    Saves or updates subject marks for a student.
    marks_dict = {"physics": float, "chemistry": float, "maths": float, "english": float, "cs_ip": float}
    Returns (success: bool, message: str)
    """
    roll_str = str(roll_no).strip()
    student = get_student_by_roll(roll_str)
    if not student:
        return False, f"Cannot save marks: Student with Roll Number {roll_str} does not exist."

    _SAMPLE_MARKS[roll_str] = marks_dict
    return True, f"Marks saved successfully for Roll Number {roll_str}."


def get_marks(roll_no):
    """
    Fetches marks dictionary for a student by Roll Number.
    Returns dict or None.
    """
    roll_str = str(roll_no).strip()
    return _SAMPLE_MARKS.get(roll_str, None)


def get_result(roll_no):
    """
    Calculates and returns complete result report for a student.
    Returns result dict with student details, marks, total, percentage, grade, status.
    """
    roll_str = str(roll_no).strip()
    student = get_student_by_roll(roll_str)
    if not student:
        return None

    marks = get_marks(roll_str)
    if not marks:
        return {
            "student": student,
            "has_marks": False,
            "message": "Marks have not been entered for this student yet."
        }

    p = marks.get("physics", 0)
    c = marks.get("chemistry", 0)
    m = marks.get("maths", 0)
    e = marks.get("english", 0)
    cs = marks.get("cs_ip", 0)

    total = p + c + m + e + cs
    percentage = round(total / 5.0, 2)

    # Class 12 Grading System
    if percentage >= 90:
        grade = "A1"
    elif percentage >= 80:
        grade = "A2"
    elif percentage >= 70:
        grade = "B1"
    elif percentage >= 60:
        grade = "B2"
    elif percentage >= 50:
        grade = "C1"
    elif percentage >= 40:
        grade = "C2"
    elif percentage >= 33:
        grade = "D"
    else:
        grade = "E (Needs Improvement)"

    # Pass / Fail criteria (minimum 33% in each subject)
    failed_subjects = []
    subject_map = {
        "Physics": p, "Chemistry": c, "Mathematics": m,
        "English": e, "Computer Science / IP": cs
    }
    for sub, score in subject_map.items():
        if score < 33:
            failed_subjects.append(sub)

    if len(failed_subjects) == 0:
        status = "PASSED"
    elif len(failed_subjects) <= 2:
        status = f"COMPARTMENT ({', '.join(failed_subjects)})"
    else:
        status = "FAILED"

    return {
        "student": student,
        "has_marks": True,
        "marks": marks,
        "total": total,
        "max_total": 500,
        "percentage": percentage,
        "grade": grade,
        "status": status,
        "failed_subjects": failed_subjects
    }
