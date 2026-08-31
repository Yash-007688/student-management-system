"""
screens/student_search.py
-------------------------
Screen to search students specifically by Roll Number or Name.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class SearchStudentScreen(ttk.Frame):
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
            text="Search Student Records",
            font=ui_styles.FONT_TITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).pack(side="left", padx=20)

        # 2. Main Content
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # Search Controls Card
        search_card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        search_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(search_card, text="Search By:", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 10))

        self.search_by_var = tk.StringVar(value="Name")
        search_by_cb = ttk.Combobox(search_card, textvariable=self.search_by_var, values=["Name", "Roll Number", "Class"], state="readonly", width=14)
        search_by_cb.pack(side="left", padx=(0, 15))

        ttk.Label(search_card, text="Keyword:", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 10))

        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(search_card, textvariable=self.query_var, width=28)
        query_entry.pack(side="left", padx=(0, 15))
        query_entry.bind("<Return>", lambda e: self._perform_search())

        search_btn = ttk.Button(
            search_card,
            text="🔍 Search",
            style="Primary.TButton",
            command=self._perform_search
        )
        search_btn.pack(side="left", padx=(0, 10))

        reset_btn = ttk.Button(
            search_card,
            text="Reset",
            style="Secondary.TButton",
            command=self._reset_search
        )
        reset_btn.pack(side="left")

        # Results Card
        results_card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        results_card.grid(row=1, column=0, sticky="nsew")
        results_card.columnconfigure(0, weight=1)
        results_card.rowconfigure(1, weight=1)

        self.results_header = ttk.Label(results_card, text="Search Results", font=ui_styles.FONT_SUBTITLE, style="Card.TLabel")
        self.results_header.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Treeview + Scrollbars
        table_frame = ttk.Frame(results_card)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("roll_no", "name", "class", "section", "gender", "phone", "email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        headings = [
            ("roll_no", "Roll No", 90),
            ("name", "Student Name", 180),
            ("class", "Class", 70),
            ("section", "Section", 70),
            ("gender", "Gender", 90),
            ("phone", "Phone", 120),
            ("email", "Email Address", 200),
        ]

        for col_id, col_name, width in headings:
            self.tree.heading(col_id, text=col_name, anchor="w")
            self.tree.column(col_id, width=width, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self._reset_search()

    def _perform_search(self):
        query = self.query_var.get().strip()
        search_by = self.search_by_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        results = database.search_students(query, search_by)
        for s in results:
            self.tree.insert("", "end", values=(
                s.get("roll_no", ""),
                s.get("name", ""),
                s.get("class", ""),
                s.get("section", ""),
                s.get("gender", ""),
                s.get("phone", ""),
                s.get("email", "")
            ))

        self.results_header.configure(text=f"Search Results ({len(results)} matches found)")

    def _reset_search(self):
        self.query_var.set("")
        self._perform_search()
