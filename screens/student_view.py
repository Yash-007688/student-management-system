"""
screens/student_view.py
-----------------------
View All Students Screen using Treeview with scrollbars & search filter.
"""

import tkinter as tk
from tkinter import ttk
import database
import ui_styles


class ViewStudentsScreen(ttk.Frame):
    def __init__(self, parent, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        # 1. Top Bar
        top_bar = ttk.Frame(self, style="Card.TFrame", padding=(20, 12))
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        back_btn = ttk.Button(
            top_bar,
            text="← Back to Dashboard",
            style="Secondary.TButton",
            command=self.on_back_callback
        )
        back_btn.pack(side="left")

        ttk.Label(
            top_bar,
            text="All Enrolled Students",
            font=ui_styles.FONT_TITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).pack(side="left", padx=20)

        # Refresh button
        refresh_btn = ttk.Button(
            top_bar,
            text="🔄 Refresh",
            style="Secondary.TButton",
            command=self.refresh_table
        )
        refresh_btn.pack(side="right")

        # 2. Main Content
        content_frame = ttk.Frame(self, style="Card.TFrame", padding=20)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # Quick Filter Bar
        filter_frame = ttk.Frame(content_frame, style="Card.TFrame")
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(filter_frame, text="Quick Filter:", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._on_filter_changed())
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=(0, 15))

        self.count_lbl = ttk.Label(filter_frame, text="Total: 0", style="CardMuted.TLabel")
        self.count_lbl.pack(side="right")

        # Treeview + Scrollbars Container
        table_frame = ttk.Frame(content_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("roll_no", "name", "class", "section", "dob", "gender", "phone", "email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Column Headings & Widths
        headings = [
            ("roll_no", "Roll No", 90),
            ("name", "Student Name", 180),
            ("class", "Class", 70),
            ("section", "Section", 70),
            ("dob", "Date of Birth", 110),
            ("gender", "Gender", 90),
            ("phone", "Phone", 120),
            ("email", "Email Address", 200),
        ]

        for col_id, col_name, width in headings:
            self.tree.heading(col_id, text=col_name, anchor="w")
            self.tree.column(col_id, width=width, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.refresh_table()

    def refresh_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        students = database.get_all_students()
        for s in students:
            self.tree.insert("", "end", values=(
                s.get("roll_no", ""),
                s.get("name", ""),
                s.get("class", ""),
                s.get("section", ""),
                s.get("dob", ""),
                s.get("gender", ""),
                s.get("phone", ""),
                s.get("email", "")
            ))
        self.count_lbl.configure(text=f"Total Records: {len(students)}")

    def _on_filter_changed(self):
        query = self.search_var.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        students = database.get_all_students()
        count = 0
        for s in students:
            if query in s.get("name", "").lower() or query in s.get("roll_no", "").lower() or query in s.get("class", "").lower():
                self.tree.insert("", "end", values=(
                    s.get("roll_no", ""),
                    s.get("name", ""),
                    s.get("class", ""),
                    s.get("section", ""),
                    s.get("dob", ""),
                    s.get("gender", ""),
                    s.get("phone", ""),
                    s.get("email", "")
                ))
                count += 1
        self.count_lbl.configure(text=f"Showing: {count} of {len(students)}")
