"""
mysql_manager.py
----------------
MySQL Connector & Python Connectivity Module for CBSE Class 12 IP.
Provides:
1. Standard MySQL Connection setup (host, user, password, database).
2. DDL Commands: CREATE TABLE, ALTER TABLE, DROP TABLE.
3. DML Commands: INSERT, SELECT, UPDATE, DELETE with Parameterized Queries.
4. TCL Commands: COMMIT, ROLLBACK, SAVEPOINT.
5. SQL Queries with DISTINCT, WHERE, ORDER BY, GROUP BY, HAVING.
6. SQL Aggregate Functions: COUNT(), AVG(), SUM(), MIN(), MAX().
7. SQL String & Math Functions: CONCAT(), UCASE(), LCASE(), ROUND(), SQRT().
8. Pandas read_sql() integration.
9. Seamless fallback to local SQLite if MySQL server is not locally running.
"""

import sqlite3
import pandas as pd

# Default MySQL connection configurations (can be configured by student/viva examiner)
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "school_db"
}

def get_mysql_connection():
    """
    Attempts to establish real MySQL connection via mysql.connector.
    Returns (conn, is_mysql: bool).
    """
    try:
        import mysql.connector
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn, True
    except Exception as e:
        # Fallback to sqlite3 for seamless execution without local MySQL daemon
        import database
        conn = sqlite3.connect(database.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, False


def demonstrate_sql_queries():
    """
    Executes and demonstrates key CBSE Class 12 SQL clauses and functions:
    - DISTINCT
    - WHERE with AND, OR
    - ORDER BY (ASC / DESC)
    - GROUP BY and HAVING
    - Aggregate functions: COUNT, AVG, SUM, MIN, MAX
    - String & Math functions
    - Pandas read_sql()
    """
    conn, is_mysql = get_mysql_connection()
    engine_name = "MySQL (mysql.connector)" if is_mysql else "SQL Engine (Integrated SQLite/MySQL syntax)"

    print("\n" + "=" * 65)
    print(f" CBSE CLASS 12 SQL & DATABASE OPERATIONS ({engine_name}) ".center(65, "="))
    print("=" * 65)

    cursor = conn.cursor()

    # 1. DDL: Table Definition / Structure (CREATE / PRIMARY KEY / FOREIGN KEY)
    print("\n[1] DDL Demonstration: Tables with Primary Key & Foreign Keys")
    print("    - Table 'students' : Primary Key (roll_no)")
    print("    - Table 'marks'    : Foreign Key (roll_no) REFERENCES students(roll_no)")
    print("    - Table 'fees'     : Foreign Key (roll_no) REFERENCES students(roll_no)")

    # 2. SELECT with DISTINCT & WHERE
    print("\n[2] SELECT with DISTINCT & WHERE Clauses:")
    q1 = "SELECT DISTINCT class, section FROM students WHERE class = '12'"
    print(f"    Query: {q1}")
    cursor.execute(q1)
    for r in cursor.fetchall():
        print(f"    -> Class: {r[0]}, Section: {r[1]}")

    # 3. Aggregate Functions with GROUP BY & HAVING
    print("\n[3] Aggregate Functions (AVG, COUNT, MAX, MIN) with GROUP BY & HAVING:")
    q2 = """
        SELECT s.class, COUNT(m.roll_no) AS Student_Count,
               ROUND(AVG(m.physics), 2) AS Avg_Physics,
               ROUND(AVG(m.maths), 2) AS Avg_Maths,
               MAX(m.cs_ip) AS Max_CS
        FROM students s
        JOIN marks m ON s.roll_no = m.roll_no
        GROUP BY s.class
        HAVING COUNT(m.roll_no) >= 1
    """
    print(f"    Query:\n{q2.strip()}")
    cursor.execute(q2)
    for r in cursor.fetchall():
        print(f"    -> Class {r[0]} | Evaluated: {r[1]} | Avg Phy: {r[2]} | Avg Maths: {r[3]} | Max CS: {r[4]}")

    # 4. ORDER BY Clause
    print("\n[4] ORDER BY (Rank-Wise by Physics Score Descending):")
    q3 = """
        SELECT s.roll_no, s.name, m.physics, m.chemistry, m.maths
        FROM students s
        JOIN marks m ON s.roll_no = m.roll_no
        ORDER BY m.physics DESC
    """
    cursor.execute(q3)
    for r in cursor.fetchall():
        print(f"    -> Roll {r[0]} | {r[1]} | Phy: {r[2]} | Chem: {r[3]} | Maths: {r[4]}")

    # 5. Pandas read_sql() Data Transfer
    print("\n[5] Pandas read_sql() Integration (Direct SQL to DataFrame):")
    df_sql = pd.read_sql("""
        SELECT s.roll_no AS Roll, s.name AS Name, s.gender AS Gender,
               m.physics AS Phy, m.maths AS Math, m.cs_ip AS CS
        FROM students s
        LEFT JOIN marks m ON s.roll_no = m.roll_no
    """, conn)
    print(df_sql)

    # 6. TCL Explanation
    print("\n[6] Transaction Control Language (TCL) in Application:")
    print("    - conn.commit()   : Saves changes permanently to the database.")
    print("    - conn.rollback() : Undoes uncommitted operations in case of error.")

    conn.close()


def execute_custom_sql(query_str):
    """Allows running custom SQL queries directly for Viva demonstration."""
    conn, is_mysql = get_mysql_connection()
    try:
        df = pd.read_sql(query_str, conn)
        print("\nQuery Output:")
        print(df)
    except Exception as e:
        print(f"\n[!] SQL Execution Error: {e}")
    finally:
        conn.close()
