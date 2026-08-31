# Student Management System
### Class 12 Python Project — by Yash

---

## Project Overview

A desktop application built using **Python + Tkinter** for managing student records, marks, and results. The app has a clean professional UI and uses an in-memory database (ready to swap with SQLite).

---

## How to Run

```
python main.py
```

**Default Login:**
- Username: `admin`
- Password: `admin123`

---

## Features

| Screen | What it does |
|---|---|
| Login | Secure login with show/hide password |
| Dashboard | Overview with total students + quick navigation |
| Add Student | Register new student with form validation |
| View All Students | Treeview table with live search filter |
| Search Student | Search by Name, Roll Number, or Class |
| Update Student | Fetch by Roll No, edit and save changes |
| Marks Entry | Enter/update subject marks per student |
| Result / Report | Auto-calculates total, percentage, grade, pass/fail |

---

## Project Structure

```
school project/
│
├── main.py              ← Entry point, screen navigation
├── database.py          ← Data layer (CRUD + marks + results)
├── ui_styles.py         ← Colors, fonts, ttk styling
│
└── screens/
    ├── __init__.py
    ├── login.py
    ├── dashboard.py
    ├── student_add.py
    ├── student_view.py
    ├── student_search.py
    ├── student_update.py
    ├── marks_entry.py
    └── result_view.py
```

---

## Subjects Covered

- Physics
- Chemistry
- Mathematics
- English
- Computer Science / Informatics Practices

---

## Grading System

| Percentage | Grade |
|---|---|
| 90% and above | A1 |
| 80% – 89% | A2 |
| 70% – 79% | B1 |
| 60% – 69% | B2 |
| 50% – 59% | C1 |
| 40% – 49% | C2 |
| 33% – 39% | D |
| Below 33% | E (Needs Improvement) |

Pass criteria: minimum **33 marks** in each subject.
- 0 failed subjects → **PASSED**
- 1–2 failed subjects → **COMPARTMENT**
- 3+ failed subjects → **FAILED**

---

## Tech Used

- Python 3
- Tkinter / ttk (GUI)
- In-memory data store (replaceable with SQLite)

---

## Notes

- No third-party libraries needed
- All UI and app logic by Yash
- Database layer (`database.py`) is kept separate for easy SQLite integration later

---

> Made by **building_void**
