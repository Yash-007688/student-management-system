# Student Management System — CBSE Class 12 Informatics Practices (IP) Project

An end-to-end Python desktop application created strictly according to the **CBSE Class 12 Informatics Practices (065)** syllabus.

---

## 🎯 Syllabus Topics Covered

### 1. Data Handling using Pandas
- **Series**: Creation (from list, dictionary), Indexing, Slicing, Operations (+, -, *, /), Attributes (`shape`, `size`, `index`, `values`, `ndim`, `empty`).
- **DataFrame**:
  - Creation & Inspection (`shape`, `size`, `dtypes`, `index`, `columns`, `head()`, `tail()`)
  - Indexing & Slicing using `.loc[]` and `.iloc[]`
  - Iteration using `iterrows()`
  - Manipulations: Adding/Deleting columns (`drop`), updating values, renaming (`rename`)
  - Summary functions: `count()`, `sum()`, `mean()`, `min()`, `max()`, `isnull()`
  - Boolean Filtering & Sorting (`sort_values`)
- **CSV Data Transfer**: `read_csv()`, `to_csv()` with parameters (`skiprows`, `header`, `index_col`, `nrows`, `names`).

### 2. Data Visualisation using Matplotlib Pyplot
- **Line Chart**: Progress trend with custom markers, linestyles, colors, and grid.
- **Bar Chart**: Subject-wise scores with benchmark reference line (`axhline`).
- **Histogram**: Frequency distribution of marks in score bins.
- **Scatter Plot**: Correlation analysis (Physics vs Mathematics).
- **Box Plot**: Subject-wise marks spread and quartiles.
- **Pie Chart**: Pass / Compartment / Fail distribution with `autopct`, `explode`, shadow, colors.
- **Multiple Subplots**: 2x2 multi-panel analytical dashboard (`plt.subplots()`).

### 3. Database Management (SQL & MySQL Connectivity)
- **Keys**: Primary Key, Candidate Key, Alternate Key, Foreign Key.
- **SQL Clauses**: `DISTINCT`, `WHERE`, `ORDER BY`, `GROUP BY`, `HAVING`.
- **Aggregate Functions**: `COUNT()`, `AVG()`, `SUM()`, `MIN()`, `MAX()`.
- **TCL**: `COMMIT`, `ROLLBACK`, `SAVEPOINT`.
- **Python Connectivity**: `mysql.connector` & Pandas `pd.read_sql()`.

### 4. Societal Impacts & Computer Networks (Viva Revision)
- **Cyber Safety**: Cybercrime, Phishing, Identity Theft, Password best practices, Digital Footprint.
- **E-Waste Management**: Hazards and solutions (Reduce, Reuse, Recycle).
- **Computer Networks**: LAN, MAN, WAN, Topologies (Star, Bus, Tree), Devices (Hub, Switch, Router, Modem, Gateway).

---

## 📁 Project Architecture

```text
school project/
├── main.py            # Main entry point with role-based dashboards
├── data_analysis.py   # Pandas Series & DataFrame analysis module
├── charts.py          # Matplotlib Pyplot visualisation module
├── mysql_manager.py   # MySQL connector & Python-SQL queries
├── database.py        # Core database layer (SQLite / SQL engine)
├── viva_theory.py     # Class 12 IP Theory & Viva guide
├── students_data.csv  # Auto-synchronized CSV dataset
└── school.db          # Database file
```

---

## 🚀 How to Run

```bash
python main.py
```

### Default Login Accounts:
- **Admin**: `admin` / `admin123`
- **Teacher**: `teacher` / `teacher123`
- **Student**: `student` / `student123`
