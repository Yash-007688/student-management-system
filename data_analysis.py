"""
data_analysis.py
----------------
CBSE Class 12 Informatics Practices (IP) — Data Analysis Module.
Covers core syllabus concepts:
- Pandas Series & DataFrame creation, indexing & slicing (.loc[], .iloc[])
- Attributes: shape, size, index, columns, dtypes, ndim, empty
- Summary functions: head(), tail(), min(), max(), sum(), mean(), count()
- Handling missing values: isnull(), notnull()
- DataFrame iterations: iterrows(), itertuples()
- DataFrame manipulation: adding/deleting columns & rows, updating, renaming
- Filtering & Sorting (sort_values)
- CSV transfer: read_csv(), to_csv() with skiprows, names, index_col, nrows
- Mathematical & aggregate computations
"""

import os
import pandas as pd
import numpy as np
import database

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students_data.csv")


# ── 1. Data Export & CSV Transfer (to_csv / read_csv) ───────────────────────

def export_db_to_csv(filepath=CSV_FILE):
    """
    Fetches students + marks from database and exports to CSV using pandas.to_csv().
    Demonstrates: DataFrame creation, DataFrame export to CSV.
    """
    students = database.get_all_students()
    if not students:
        return False, "No student records to export."

    records = []
    for s in students:
        res = database.get_result(s["roll_no"])
        m = res.get("marks", {}) if (res and res.get("has_marks")) else {}
        records.append({
            "RollNo": s.get("roll_no"),
            "Name": s.get("name"),
            "Class": s.get("class"),
            "Section": s.get("section"),
            "Gender": s.get("gender"),
            "Phone": s.get("phone"),
            "Physics": m.get("physics", np.nan),
            "Chemistry": m.get("chemistry", np.nan),
            "Maths": m.get("maths", np.nan),
            "English": m.get("english", np.nan),
            "CS_IP": m.get("cs_ip", np.nan),
            "Total": res.get("total", np.nan) if res else np.nan,
            "Percentage": res.get("percentage", np.nan) if res else np.nan,
            "Grade": res.get("grade", "N/A") if res else "N/A",
            "Status": res.get("status", "N/A") if res else "N/A",
        })

    df = pd.DataFrame(records)
    df.to_csv(filepath, index=False)
    return True, f"Data successfully exported to '{os.path.basename(filepath)}' ({len(df)} rows)."


def load_dataframe_from_csv(filepath=CSV_FILE, **kwargs):
    """
    Reads student dataset with options demonstrating read_csv() parameters:
    skiprows, header, names, index_col, nrows, sep.
    """
    if not os.path.exists(filepath):
        export_db_to_csv(filepath)
    return pd.read_csv(filepath, **kwargs)


def get_current_df():
    """Returns the main working DataFrame synced from database."""
    export_db_to_csv(CSV_FILE)
    return pd.read_csv(CSV_FILE)


# ── 2. Series & DataFrame Demonstrations (CBSE Class 12 IP) ─────────────────

def demo_series_operations():
    """
    Demonstrates:
    - Series Creation (from list, dict, scalar)
    - Series Indexing & Slicing
    - Series Attributes (index, values, shape, size, ndim, empty)
    - Mathematical operations (+, -, *, /)
    - Head & Tail
    """
    print("\n" + "=" * 60)
    print(" 1. PANDAS SERIES CREATION & OPERATIONS ".center(60, "="))
    print("=" * 60)

    # 1. Series from List
    subjects = ["Physics", "Chemistry", "Maths", "English", "CS_IP"]
    marks = [85, 92, 78, 88, 95]
    s_marks = pd.Series(marks, index=subjects, name="Sample_Marks")
    print("\n[A] Series Created from List with Custom Index:")
    print(s_marks)

    # 2. Series from Dictionary
    fees_dict = {"101": 12000, "102": 10000, "103": 12000}
    s_fees = pd.Series(fees_dict, name="Fees_Paid")
    print("\n[B] Series Created from Dictionary:")
    print(s_fees)

    # 3. Series Attributes
    print("\n[C] Series Attributes:")
    print(f"  - s_marks.index   : {list(s_marks.index)}")
    print(f"  - s_marks.values  : {s_marks.values}")
    print(f"  - s_marks.shape   : {s_marks.shape}")
    print(f"  - s_marks.size    : {s_marks.size}")
    print(f"  - s_marks.ndim    : {s_marks.ndim}")
    print(f"  - s_marks.empty   : {s_marks.empty}")

    # 4. Indexing & Slicing
    print("\n[D] Indexing & Slicing:")
    print(f"  - Single index label ['Maths'] : {s_marks['Maths']}")
    print(f"  - Positional index [0]        : {s_marks.iloc[0]}")
    print(f"  - Slicing ['Physics':'Maths'] :\n{s_marks['Physics':'Maths']}")

    # 5. Mathematical Operations (Vectorized)
    print("\n[E] Vectorized Mathematical Operations (+5 Grace Marks):")
    print(s_marks + 5)

    # 6. Statistical Functions
    print("\n[F] Series Statistical / Aggregation Functions:")
    print(f"  - Max Mark : {s_marks.max()} (in {s_marks.idxmax()})")
    print(f"  - Min Mark : {s_marks.min()} (in {s_marks.idxmin()})")
    print(f"  - Average  : {s_marks.mean():.2f}")
    print(f"  - Total    : {s_marks.sum()}")
    print(f"  - Count    : {s_marks.count()}")


def show_dataframe_attributes():
    """
    Shows DataFrame inspection attributes:
    shape, size, dtypes, index, columns, ndim, empty.
    """
    df = get_current_df()
    print("\n" + "=" * 60)
    print(" 2. DATAFRAME ATTRIBUTES & INSPECTION ".center(60, "="))
    print("=" * 60)
    print(f"DataFrame Shape (Rows, Cols) : {df.shape}")
    print(f"DataFrame Size (Total Cells) : {df.size}")
    print(f"Dimensions (ndim)            : {df.ndim}")
    print(f"Is Empty?                    : {df.empty}")
    print(f"\nIndex Range                  : {df.index}")
    print(f"Columns List                 : {list(df.columns)}")
    print("\nData Types (dtypes):\n" + str(df.dtypes))
    print("\nFirst 3 Records (head(3)):\n" + str(df.head(3)))
    print("\nLast 2 Records (tail(2)):\n" + str(df.tail(2)))


def show_dataframe_indexing_slicing():
    """
    Demonstrates loc[] and iloc[]:
    - Label-based indexing: loc[row_label, col_label]
    - Position-based indexing: iloc[row_pos, col_pos]
    """
    df = get_current_df()
    print("\n" + "=" * 60)
    print(" 3. DATAFRAME INDEXING & SLICING (loc[] & iloc[]) ".center(60, "="))
    print("=" * 60)

    print("\n[A] Access using loc[] (Label-based):")
    try:
        # First row, selected columns
        subset_loc = df.loc[0:2, ["RollNo", "Name", "Class", "Percentage", "Grade"]]
        print(subset_loc)
    except Exception as e:
        print(f"Error in loc: {e}")

    print("\n[B] Access using iloc[] (Integer positional index):")
    try:
        # Rows 0 to 1, first 4 columns
        subset_iloc = df.iloc[0:2, 0:4]
        print(subset_iloc)
    except Exception as e:
        print(f"Error in iloc: {e}")

    print("\n[C] Single Value Extraction:")
    if len(df) > 0:
        print(f"  - df.loc[0, 'Name'] : {df.loc[0, 'Name']}")
        print(f"  - df.iloc[0, 1]     : {df.iloc[0, 1]}")


def show_summary_and_aggregations():
    """
    Demonstrates aggregate functions:
    count(), sum(), mean(), min(), max(), isnull()
    """
    df = get_current_df()
    subject_cols = ["Physics", "Chemistry", "Maths", "English", "CS_IP", "Total", "Percentage"]
    print("\n" + "=" * 60)
    print(" 4. MATHEMATICAL & AGGREGATE FUNCTIONS ".center(60, "="))
    print("=" * 60)

    avail_cols = [c for c in subject_cols if c in df.columns]
    print("\n[A] Statistical Summary of Numerical Columns:")
    stats_df = pd.DataFrame({
        "Count": df[avail_cols].count(),
        "Mean": df[avail_cols].mean().round(2),
        "Min": df[avail_cols].min(),
        "Max": df[avail_cols].max(),
        "Sum": df[avail_cols].sum()
    })
    print(stats_df)

    print("\n[B] Missing Values Check (isnull().sum()):")
    print(df[avail_cols].isnull().sum())


def show_filtering_and_sorting():
    """
    Demonstrates Boolean Indexing / Filtering & Sorting:
    - Multiple conditions (&, |)
    - df.sort_values(by, ascending)
    """
    df = get_current_df()
    print("\n" + "=" * 60)
    print(" 5. FILTERING & SORTING DATAFRAME ".center(60, "="))
    print("=" * 60)

    print("\n[A] Filtering: Students scoring Percentage >= 80%:")
    high_scorers = df[df["Percentage"] >= 80][["RollNo", "Name", "Percentage", "Grade"]]
    print(high_scorers if not high_scorers.empty else "No students with >=80%")

    print("\n[B] Filtering: Gender == 'Female' OR Percentage > 85:")
    cond_filter = df[(df["Gender"] == "Female") | (df["Percentage"] > 85)][["RollNo", "Name", "Gender", "Percentage"]]
    print(cond_filter)

    print("\n[C] Sorting: Sorted by Percentage (Descending - Rank wise):")
    sorted_df = df.sort_values(by="Percentage", ascending=False)[["RollNo", "Name", "Percentage", "Grade"]]
    print(sorted_df)


def show_dataframe_iteration():
    """
    Demonstrates iterrows() loop over DataFrame rows.
    """
    df = get_current_df()
    print("\n" + "=" * 60)
    print(" 6. DATAFRAME ITERATION (iterrows()) ".center(60, "="))
    print("=" * 60)

    for index, row in df.head(3).iterrows():
        print(f"Row {index} -> Roll: {row.get('RollNo')} | Name: {row.get('Name')} | %: {row.get('Percentage')}% | Grade: {row.get('Grade')}")


def demo_df_manipulation():
    """
    Demonstrates:
    - Adding new column
    - Renaming column
    - Updating values
    - Deleting column (drop)
    """
    df = get_current_df().copy()
    print("\n" + "=" * 60)
    print(" 7. DATAFRAME MANIPULATION (Add/Delete/Rename/Update) ".center(60, "="))
    print("=" * 60)

    # 1. Adding a Column
    df["Result_Remark"] = np.where(df["Percentage"] >= 75, "Distinction", "Regular")
    print("\n[A] Added new column 'Result_Remark':")
    print(df[["RollNo", "Name", "Percentage", "Result_Remark"]].head(3))

    # 2. Updating values
    df.loc[df["Grade"] == "A1", "Result_Remark"] = "Scholar Star"
    print("\n[B] Updated 'Result_Remark' for Grade A1:")
    print(df[["RollNo", "Name", "Grade", "Result_Remark"]].head(3))

    # 3. Renaming Column
    df.rename(columns={"Result_Remark": "Performance_Category"}, inplace=True)
    print("\n[C] Renamed column to 'Performance_Category':")
    print(df.columns.tolist())

    # 4. Deleting a Column
    df.drop(columns=["Performance_Category"], inplace=True)
    print("\n[D] Deleted (dropped) 'Performance_Category' column successfully.")
