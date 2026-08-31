"""
screens/marks_entry.py
----------------------
Screen to enter/update subject marks for students.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class MarksEntryScreen(ttk.Frame):
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
            text="Enter/Update Student Marks",
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

        ttk.Label(fetch_card, text="Enter Roll Number:", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 10))
        self.fetch_roll_var = tk.StringVar()
        fetch_entry = ttk.Entry(fetch_card, textvariable=self.fetch_roll_var, width=20)
        fetch_entry.pack(side="left", padx=(0, 15))
        fetch_entry.bind("<Return>", lambda e: self._fetch_student())

        fetch_btn = ttk.Button(
            fetch_card,
            text="🔍 Fetch Marks",
            style="Primary.TButton",
            command=self._fetch_student
        )
        fetch_btn.pack(side="left")

        # Marks Form Card
        self.form_card = ttk.Frame(content_frame, style="Card.TFrame", padding=25)
        self.form_card.pack(fill="both", expand=True)

        ttk.Label(
            self.form_card,
            text="Subject Marks Entry (Out of 100)",
            font=ui_styles.FONT_SUBTITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Subject Fields
        subjects = [
            ("Physics", "physics"),
            ("Chemistry", "chemistry"),
            ("Mathematics", "maths"),
            ("English", "english"),
            ("Computer Science / IP", "cs_ip"),
        ]

        self.marks_inputs = {}

        for i, (label_text, key) in enumerate(subjects):
            row_idx = i + 1

            ttk.Label(self.form_card, text=label_text, font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").grid(
                row=row_idx, column=0, sticky="w", padx=(10, 10), pady=(8, 2)
            )

            var = tk.StringVar()
            entry = ttk.Entry(self.form_card, textvariable=var, width=15)
            entry.grid(row=row_idx, column=1, sticky="ew", padx=(10, 10), pady=(0, 12))
            self.marks_inputs[key] = var

        self.form_card.columnconfigure(0, weight=1)
        self.form_card.columnconfigure(1, weight=1)

        # Action Buttons
        btn_frame = ttk.Frame(self.form_card, style="Card.TFrame")
        btn_frame.grid(row=10, column=0, columnspan=2, sticky="w", pady=(25, 0))

        self.save_btn = ttk.Button(
            btn_frame,
            text="💾 Save Marks",
            style="Success.TButton",
            command=self._save_marks,
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        self.status_lbl = ttk.Label(btn_frame, text="Fetch a student to enter marks.", style="CardMuted.TLabel")
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

        # Load existing marks if available
        existing_marks = database.get_marks(roll)
        if existing_marks:
            self.marks_inputs["physics"].set(existing_marks.get("physics", ""))
            self.marks_inputs["chemistry"].set(existing_marks.get("chemistry", ""))
            self.marks_inputs["maths"].set(existing_marks.get("maths", ""))
            self.marks_inputs["english"].set(existing_marks.get("english", ""))
            self.marks_inputs["cs_ip"].set(existing_marks.get("cs_ip", ""))
            self.status_lbl.configure(text=f"Editing marks for: {student.get('name')} (Roll: {roll})")
        else:
            self._clear_form()
            self.status_lbl.configure(text=f"Enter marks for: {student.get('name')} (Roll: {roll})")

        self.save_btn.configure(state="normal")

    def _clear_form(self):
        for var in self.marks_inputs.values():
            var.set("")

    def _save_marks(self):
        if not self.loaded_roll:
            return

        try:
            marks = {
                "physics": float(self.marks_inputs["physics"].get().strip() or 0),
                "chemistry": float(self.marks_inputs["chemistry"].get().strip() or 0),
                "maths": float(self.marks_inputs["maths"].get().strip() or 0),
                "english": float(self.marks_inputs["english"].get().strip() or 0),
                "cs_ip": float(self.marks_inputs["cs_ip"].get().strip() or 0),
            }
        except ValueError:
            messagebox.showwarning("Validation Error", "Please enter valid numeric marks for all subjects.")
            return

        # Validate marks range
        for subject, score in marks.items():
            if score < 0 or score > 100:
                messagebox.showwarning("Validation Error", f"{subject} marks must be between 0 and 100.")
                return

        success, msg = database.save_marks(self.loaded_roll, marks)
        if success:
            messagebox.showinfo("Success", msg)
            self.status_lbl.configure(text="Marks saved successfully!")
        else:
            messagebox.showerror("Error", msg)
