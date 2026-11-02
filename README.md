# Student Management System — CBSE Class 12 Informatics Practices (IP) Project

An end-to-end Python desktop application created strictly according to the **CBSE Class 12 Informatics Practices (065)** syllabus.

---

## 🎯 Project Overview & Architecture

- **Primary Application Database**: SQLite database (`school.db`) with full transactional integrity (`conn.commit()`), ACID compliance, and foreign key constraints.
- **MySQL Connectivity Module**: Python–MySQL connectivity demonstration via `mysql.connector` with fallback to the local SQL engine (`mysql_manager.py`).
- **Data Analysis**: Pandas Series & DataFrames with `.loc[]`, `.iloc[]`, filtering, sorting, aggregations, and CSV export.
- **Data Visualisation**: 100% Real-Time Matplotlib Pyplot charts without synthetic or hard-coded figures.

```text
school project/
├── main.py            # Main entry point with role-based dashboards (Admin, Teacher, Student)
├── data_analysis.py   # Pandas Series & DataFrame analysis module
├── charts.py          # Real-time Matplotlib Pyplot visualisation module
├── mysql_manager.py   # MySQL connector & Python-SQL queries
├── database.py        # Core database layer with strict role security
├── viva_theory.py     # Class 12 IP Theory & Viva revision guide
├── requirements.txt   # Environment dependency specifications
├── students_data.csv  # Auto-synchronized CSV dataset
└── school.db          # SQLite Database file
```

---

## 📦 Installation & Setup

Ensure Python 3.8+ is installed on the system.

1. **Clone repository / Navigate to directory**:
   ```bash
   cd "school project"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run application**:
   ```bash
   python main.py
   ```

---

## 🔑 Official Login Credentials & Access Scopes

| Role | Username | Password | Linked Entity / Scope | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Universal | Full system administration, user management, CRUD, fees, and analytics. |
| **Teacher** | `teacher` | `teacher123` | Class `12-A` | Restricted strictly to Class 12-A students for search, marks, and results. |
| **Student** | `aarav` | `aarav123` | Roll No `101` | Private view: Aarav Sharma (Class 12-A). |
| **Student** | `diya` | `diya123` | Roll No `102` | Private view: Diya Patel (Class 12-A). |
| **Student** | `rohan` | `rohan123` | Roll No `103` | Private view: Rohan Verma (Class 12-B). |
| **Student** | `priya` | `priya123` | Roll No `104` | Private view: Priya Singh (Class 12-A). |
| **Student** | `aditya` | `aditya12` | Roll No `105` | Private view: Aditya Roy (Class 12-B). |

---

## 🛡️ Access Control & Security Guarantees

1. **Teacher Scope Enforcement**:
   - A teacher assigned to Class 12-A is prevented at the database layer (`check_teacher_scope()`) from searching, updating, or editing marks/results for any student outside Class 12-A (e.g. Roll 103 / 105 in Class 12-B).
2. **Student Privacy Isolation**:
   - Both `get_result()` and `get_fees_by_roll()` enforce ownership verification: any student querying another student's roll number receives `None` (Access Denied).
3. **Transaction & Payment Validation**:
   - Fee payments reject negative values and non-positive numbers (`amount_paid <= 0`).

---

## 📊 100% Real-Time Pyplot Visualisations

All visualisations in `charts.py` are strictly calculated from live database records:
1. **Vertical Bar Chart**: Student subject-wise performance vs pass benchmark.
2. **Line Chart**: Real student scores compared against actual class averages.
3. **Histogram**: True distribution of percentages across student records.
4. **Scatter Plot**: Physics vs Mathematics score correlation.
5. **Box Plot**: Subject-wise dispersion and quartiles (compatible across all Matplotlib versions).
6. **Pie Charts**: Real-time pass/fail status and fees collection breakdown.
7. **2x2 Multi-Panel Dashboard**: Four integrated subplots generated from the live dataset.
