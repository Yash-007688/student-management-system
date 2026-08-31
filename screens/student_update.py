"""
screens/student_update.py
-------------------------
Screen to search, fetch, modify and update existing student records.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class UpdateStudentScreen(ttk.Frame):
    def __init__(self, parent, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback
        self.loaded_roll = None

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
            text="Update Student Record",
            font=ui_styles.FONT_TITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).pack(side="left", padx=20)

        # 2. Main Content Frame
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)

        # Search / Fetch Card
        fetch_card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        fetch_card.pack(fill="x", pady=(0, 15))

        ttk.Label(fetch_card, text="Enter Roll Number to Fetch:", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 10))
        self.fetch_roll_var = tk.StringVar()
        fetch_entry = ttk.Entry(fetch_card, textvariable=self.fetch_roll_var, width=20)
        fetch_entry.pack(side="left", padx=(0, 15))
        fetch_entry.bind("<Return>", lambda e: self._fetch_student())

        fetch_btn = ttk.Button(
            fetch_card,
            text="🔍 Fetch Details",
            style="Primary.TButton",
            command=self._fetch_student
        )
        fetch_btn.pack(side="left")

        # Edit Form Card
        self.form_card = ttk.Frame(content_frame, style="Card.TFrame", padding=25)
        self.form_card.pack(fill="both", expand=True)

        ttk.Label(
            self.form_card,
            text="Student Details (Edit and Save)",
            font=ui_styles.FONT_SUBTITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))

        fields = [
            ("Roll Number (Read-only)", "roll_no", "entry_disabled"),
            ("Full Name *", "name", "entry"),
            ("Class *", "class", "combobox_class"),
            ("Section *", "section", "combobox_sec"),
            ("Date of Birth (YYYY-MM-DD)", "dob", "entry"),
            ("Gender *", "gender", "combobox_gender"),
            ("Phone Number", "phone", "entry"),
            ("Email Address", "email", "entry"),
        ]

        self.inputs = {}

        for i, (label_text, key, widget_type) in enumerate(fields):
            row_idx = (i // 2) + 1
            col_offset = (i % 2) * 2

            lbl = ttk.Label(self.form_card, text=label_text, font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel")
            lbl.grid(row=row_idx, column=col_offset, sticky="w", padx=(10 if col_offset > 0 else 0, 10), pady=(8, 2))

            if widget_type == "entry_disabled":
                var = tk.StringVar()
                widget = ttk.Entry(self.form_card, textvariable=var, width=30, state="disabled")
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

            elif widget_type == "entry":
                var = tk.StringVar()
                widget = ttk.Entry(self.form_card, textvariable=var, width=30)
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

            elif widget_type == "combobox_class":
                var = tk.StringVar()
                widget = ttk.Combobox(self.form_card, textvariable=var, values=["1","2","3","4","5","6","7","8","9","10","11","12"], state="readonly", width=28)
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

            elif widget_type == "combobox_sec":
                var = tk.StringVar()
                widget = ttk.Combobox(self.form_card, textvariable=var, values=["A", "B", "C"], state="readonly", width=28)
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

            elif widget_type == "combobox_gender":
                var = tk.StringVar()
                widget = ttk.Combobox(self.form_card, textvariable=var, values=["Male", "Female", "Other"], state="readonly", width=28)
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

        self.form_card.columnconfigure(0, weight=1)
        self.form_card.columnconfigure(2, weight=1)

        # Action Buttons
        btn_frame = ttk.Frame(self.form_card, style="Card.TFrame")
        btn_frame.grid(row=10, column=0, columnspan=3, sticky="w", pady=(25, 0))

        self.save_btn = ttk.Button(
            btn_frame,
            text="💾 Save Updated Changes",
            style="Success.TButton",
            command=self._save_changes,
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        self.status_lbl = ttk.Label(btn_frame, text="Fetch a student to enable editing.", style="CardMuted.TLabel")
        self.status_lbl.pack(side="left", padx=10)

    def _fetch_student(self):
        roll = self.fetch_roll_var.get().strip()
        if not roll:
            messagebox.showwarning("Input Needed", "Please enter a Roll Number to fetch.")
            return

        student = database.get_student_by_roll(roll)
        if not student:
            messagebox.showerror("Not Found", f"No student found with Roll Number '{roll}'.")
            self._clear_form()
            self.save_btn.configure(state="disabled")
            self.status_lbl.configure(text="No student record loaded.")
            return

        self.loaded_roll = roll
        self.inputs["roll_no"].set(student.get("roll_no", ""))
        self.inputs["name"].set(student.get("name", ""))
        self.inputs["class"].set(student.get("class", "12"))
        self.inputs["section"].set(student.get("section", "A"))
        self.inputs["dob"].set(student.get("dob", ""))
        self.inputs["gender"].set(student.get("gender", "Male"))
        self.inputs["phone"].set(student.get("phone", ""))
        self.inputs["email"].set(student.get("email", ""))

        self.save_btn.configure(state="normal")
        self.status_lbl.configure(text=f"Editing student: {student.get('name')}")

    def _clear_form(self):
        for var in self.inputs.values():
            var.set("")
        self.loaded_roll = None

    def _save_changes(self):
        if not self.loaded_roll:
            return

        name = self.inputs["name"].get().strip()
        cls = self.inputs["class"].get().strip()
        sec = self.inputs["section"].get().strip()
        dob = self.inputs["dob"].get().strip()
        gender = self.inputs["gender"].get().strip()
        phone = self.inputs["phone"].get().strip()
        email = self.inputs["email"].get().strip()

        if not name or not cls or not sec:
            messagebox.showwarning("Validation Error", "Please fill in all mandatory fields (*).")
            return

        updated_data = {
            "roll_no": self.loaded_roll,
            "name": name,
            "class": cls,
            "section": sec,
            "dob": dob,
            "gender": gender,
            "phone": phone,
            "email": email
        }

        success, msg = database.update_student(self.loaded_roll, updated_data)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
