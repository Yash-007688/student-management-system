"""
screens/teacher_dashboard.py
-----------------------------
Dashboard for Teacher role — shows assigned class students, marks entry, results.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class TeacherDashboard(ttk.Frame):
    def __init__(self, parent, logout_callback, user_info):
        super().__init__(parent)
        self.logout_callback = logout_callback
        self.user_info = user_info
        self.assigned_class   = user_info.get("assigned_class", "")
        self.assigned_section = user_info.get("assigned_section", "")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self, style="Card.TFrame", padding=(25, 14))
        top.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        ttk.Label(top,
                  text=f"Welcome, {self.user_info.get('display_name')} 👋",
                  font=ui_styles.FONT_TITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").pack(side="left")

        ttk.Label(top,
                  text=f"Class {self.assigned_class} - {self.assigned_section}  |  Teacher Portal",
                  style="CardMuted.TLabel").pack(side="left", padx=16)

        ttk.Button(top, text="🚪 Logout",
                   style="Danger.TButton",
                   command=self.logout_callback).pack(side="right")

        # Main content
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        # Stats row
        stats = ttk.Frame(content, style="Card.TFrame", padding=(20, 14))
        stats.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        students = database.get_students_by_class(
            self.assigned_class, self.assigned_section)

        self.count_lbl = ttk.Label(
            stats,
            text=f"Total Students in Class {self.assigned_class}-{self.assigned_section}: {len(students)}",
            font=("Segoe UI", 16, "bold"),
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel")
        self.count_lbl.pack(side="left")

        ttk.Button(stats, text="🔄 Refresh",
                   style="Secondary.TButton",
                   command=self.refresh_data).pack(side="right")

        # Tabbed section: Students | Marks Entry
        notebook = ttk.Notebook(content)
        notebook.grid(row=1, column=0, sticky="nsew")

        self._build_students_tab(notebook)
        self._build_marks_tab(notebook)
        self._build_results_tab(notebook)

    # ── Tab 1: Students ──────────────────────────────────────────────
    def _build_students_tab(self, nb):
        tab = ttk.Frame(nb, padding=15)
        nb.add(tab, text="👨‍🎓  My Students")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        tf = ttk.Frame(tab)
        tf.grid(row=0, column=0, sticky="nsew")
        tf.columnconfigure(0, weight=1)
        tf.rowconfigure(0, weight=1)

        cols = ("roll_no","name","class","section","gender","phone","email")
        self.stu_tree = ttk.Treeview(tf, columns=cols,
                                     show="headings", selectmode="browse")
        heads = [("roll_no","Roll No",80),("name","Name",180),
                 ("class","Class",60),("section","Sec",50),
                 ("gender","Gender",80),("phone","Phone",110),
                 ("email","Email",200)]
        for cid,cname,cw in heads:
            self.stu_tree.heading(cid, text=cname, anchor="w")
            self.stu_tree.column(cid, width=cw, anchor="w")

        vsb = ttk.Scrollbar(tf, orient="vertical",
                            command=self.stu_tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal",
                            command=self.stu_tree.xview)
        self.stu_tree.configure(yscrollcommand=vsb.set,
                                xscrollcommand=hsb.set)
        self.stu_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self._load_students()

    def _load_students(self):
        for item in self.stu_tree.get_children():
            self.stu_tree.delete(item)
        for s in database.get_students_by_class(
                self.assigned_class, self.assigned_section):
            self.stu_tree.insert("", "end", values=(
                s["roll_no"], s["name"], s["class"], s["section"],
                s["gender"], s["phone"], s["email"]))

    # ── Tab 2: Marks Entry ───────────────────────────────────────────
    def _build_marks_tab(self, nb):
        tab = ttk.Frame(nb, padding=20)
        nb.add(tab, text="📊  Marks Entry")

        # Fetch row
        fetch_row = ttk.Frame(tab, style="Card.TFrame", padding=15)
        fetch_row.pack(fill="x", pady=(0, 15))

        ttk.Label(fetch_row, text="Roll Number:",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").pack(side="left", padx=(0, 8))

        self.marks_roll_var = tk.StringVar()
        fe = ttk.Entry(fetch_row, textvariable=self.marks_roll_var, width=18)
        fe.pack(side="left", padx=(0, 12))
        fe.bind("<Return>", lambda e: self._fetch_marks())

        ttk.Button(fetch_row, text="🔍 Load Marks",
                   style="Primary.TButton",
                   command=self._fetch_marks).pack(side="left")

        self.marks_name_lbl = ttk.Label(fetch_row, text="",
                                        style="CardMuted.TLabel")
        self.marks_name_lbl.pack(side="left", padx=15)

        # Marks fields
        marks_card = ttk.Frame(tab, style="Card.TFrame", padding=20)
        marks_card.pack(fill="x")

        self.marks_inputs = {}
        subjects = [("Physics","physics"),("Chemistry","chemistry"),
                    ("Mathematics","maths"),("English","english"),
                    ("Computer Science / IP","cs_ip")]

        for i, (lbl, key) in enumerate(subjects):
            ttk.Label(marks_card, text=lbl,
                      font=ui_styles.FONT_BODY_BOLD,
                      style="Card.TLabel").grid(
                row=i, column=0, sticky="w", padx=(0,20), pady=6)
            var = tk.StringVar()
            ttk.Entry(marks_card, textvariable=var, width=12).grid(
                row=i, column=1, sticky="w", pady=6)
            self.marks_inputs[key] = var

        self.marks_save_btn = ttk.Button(
            marks_card, text="💾 Save Marks",
            style="Success.TButton",
            command=self._save_marks,
            state="disabled")
        self.marks_save_btn.grid(row=6, column=0, columnspan=2,
                                 sticky="w", pady=(20, 0))

        self.marks_status_lbl = ttk.Label(marks_card, text="",
                                          style="CardMuted.TLabel")
        self.marks_status_lbl.grid(row=7, column=0, columnspan=2,
                                   sticky="w", pady=(6, 0))

        self._loaded_marks_roll = None

    def _fetch_marks(self):
        roll = self.marks_roll_var.get().strip()
        if not roll:
            return

        # Verify student belongs to teacher's class
        student = database.get_student_by_roll(roll)
        if not student:
            messagebox.showerror("Not Found", f"No student with Roll No '{roll}'.")
            return
        if (student["class"] != self.assigned_class or
                student["section"] != self.assigned_section):
            messagebox.showwarning(
                "Access Denied",
                f"Roll No {roll} belongs to Class "
                f"{student['class']}-{student['section']}.\n"
                f"You can only edit Class "
                f"{self.assigned_class}-{self.assigned_section}.")
            return

        self._loaded_marks_roll = roll
        self.marks_name_lbl.configure(
            text=f"  {student['name']}")

        existing = database.get_marks(roll)
        keys = ["physics","chemistry","maths","english","cs_ip"]
        for k in keys:
            self.marks_inputs[k].set(
                existing.get(k, "") if existing else "")

        self.marks_save_btn.configure(state="normal")
        self.marks_status_lbl.configure(text="")

    def _save_marks(self):
        if not self._loaded_marks_roll:
            return
        try:
            marks = {k: float(v.get().strip() or 0)
                     for k, v in self.marks_inputs.items()}
        except ValueError:
            messagebox.showwarning("Invalid", "Enter numeric marks only.")
            return
        for k, v in marks.items():
            if v < 0 or v > 100:
                messagebox.showwarning("Invalid",
                                       f"{k} must be between 0 and 100.")
                return
        success, msg = database.save_marks(self._loaded_marks_roll, marks)
        if success:
            self.marks_status_lbl.configure(
                text=f"✅ {msg}", foreground=ui_styles.COLOR_SUCCESS)
        else:
            messagebox.showerror("Error", msg)

    # ── Tab 3: Results ───────────────────────────────────────────────
    def _build_results_tab(self, nb):
        tab = ttk.Frame(nb, padding=20)
        nb.add(tab, text="📋  Results")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        fetch_row = ttk.Frame(tab)
        fetch_row.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ttk.Label(fetch_row, text="Roll Number:",
                  font=ui_styles.FONT_BODY_BOLD).pack(side="left", padx=(0,8))
        self.res_roll_var = tk.StringVar()
        fe = ttk.Entry(fetch_row, textvariable=self.res_roll_var, width=18)
        fe.pack(side="left", padx=(0,12))
        fe.bind("<Return>", lambda e: self._fetch_result())

        ttk.Button(fetch_row, text="📋 Get Result",
                   style="Primary.TButton",
                   command=self._fetch_result).pack(side="left")

        # Result display
        self.res_frame = ttk.Frame(tab, style="Card.TFrame", padding=20)
        self.res_frame.grid(row=1, column=0, sticky="nsew")

        self.res_text = tk.Text(self.res_frame, height=20,
                                font=ui_styles.FONT_BODY,
                                bg=ui_styles.COLOR_CARD_BG,
                                relief="flat", state="disabled")
        self.res_text.pack(fill="both", expand=True)

    def _fetch_result(self):
        roll = self.res_roll_var.get().strip()
        if not roll:
            return
        student = database.get_student_by_roll(roll)
        if not student:
            messagebox.showerror("Not Found", f"No student with Roll No '{roll}'.")
            return
        if (student["class"] != self.assigned_class or
                student["section"] != self.assigned_section):
            messagebox.showwarning("Access Denied",
                                   "This student is not in your class.")
            return
        result = database.get_result(roll)
        self.res_text.configure(state="normal")
        self.res_text.delete("1.0", "end")
        if not result or not result.get("has_marks"):
            self.res_text.insert("end", "Marks not entered yet.")
        else:
            marks = result["marks"]
            txt = (
                f"Name       : {student['name']}\n"
                f"Roll No    : {student['roll_no']}\n"
                f"Class      : {student['class']} - {student['section']}\n\n"
                f"--- Subject Marks ---\n"
                f"Physics            : {marks.get('physics',0)}\n"
                f"Chemistry          : {marks.get('chemistry',0)}\n"
                f"Mathematics        : {marks.get('maths',0)}\n"
                f"English            : {marks.get('english',0)}\n"
                f"Computer Sc. / IP  : {marks.get('cs_ip',0)}\n\n"
                f"--- Summary ---\n"
                f"Total      : {result['total']} / {result['max_total']}\n"
                f"Percentage : {result['percentage']}%\n"
                f"Grade      : {result['grade']}\n"
                f"Status     : {result['status']}\n"
            )
            self.res_text.insert("end", txt)
        self.res_text.configure(state="disabled")

    # ──────────────────────────────────────────────────────────────────
    def refresh_data(self):
        self._load_students()
        students = database.get_students_by_class(
            self.assigned_class, self.assigned_section)
        self.count_lbl.configure(
            text=f"Total Students in Class "
                 f"{self.assigned_class}-{self.assigned_section}: {len(students)}")
