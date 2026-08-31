"""
screens/student_add.py
----------------------
Screen to register a new student with input validation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class AddStudentScreen(ttk.Frame):
    def __init__(self, parent, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        # 1. Top Bar with Back Button
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
            text="Add New Student",
            font=ui_styles.FONT_TITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).pack(side="left", padx=20)

        # 2. Main Form Area
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)

        form_card = ttk.Frame(content_frame, style="Card.TFrame", padding=30)
        form_card.pack(fill="both", expand=True)

        ttk.Label(
            form_card,
            text="Student Registration Form",
            font=ui_styles.FONT_SUBTITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Fields Definition
        fields = [
            ("Roll Number *", "roll_no", "entry"),
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

            # Label
            lbl = ttk.Label(form_card, text=label_text, font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel")
            lbl.grid(row=row_idx, column=col_offset, sticky="w", padx=(10 if col_offset > 0 else 0, 10), pady=(8, 2))

            # Widget
            if widget_type == "entry":
                var = tk.StringVar()
                widget = ttk.Entry(form_card, textvariable=var, width=30)
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

            elif widget_type == "combobox_class":
                var = tk.StringVar()
                widget = ttk.Combobox(form_card, textvariable=var, values=["11", "12"], state="readonly", width=28)
                widget.set("12")
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

            elif widget_type == "combobox_sec":
                var = tk.StringVar()
                widget = ttk.Combobox(form_card, textvariable=var, values=["A", "B", "C", "D"], state="readonly", width=28)
                widget.set("A")
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

            elif widget_type == "combobox_gender":
                var = tk.StringVar()
                widget = ttk.Combobox(form_card, textvariable=var, values=["Male", "Female", "Other"], state="readonly", width=28)
                widget.set("Male")
                widget.grid(row=row_idx + 1, column=col_offset, sticky="ew", padx=(10 if col_offset > 0 else 0, 10), pady=(0, 12))
                self.inputs[key] = var

        form_card.columnconfigure(0, weight=1)
        form_card.columnconfigure(2, weight=1)

        # Buttons
        btn_row = 10
        btn_frame = ttk.Frame(form_card, style="Card.TFrame")
        btn_frame.grid(row=btn_row, column=0, columnspan=3, sticky="w", pady=(25, 0))

        save_btn = ttk.Button(
            btn_frame,
            text="💾 Save Student Record",
            style="Success.TButton",
            command=self._save_student
        )
        save_btn.pack(side="left", padx=(0, 10))

        clear_btn = ttk.Button(
            btn_frame,
            text="🔄 Clear Form",
            style="Secondary.TButton",
            command=self._clear_form
        )
        clear_btn.pack(side="left")

    def _clear_form(self):
        for key, var in self.inputs.items():
            if key == "class":
                var.set("12")
            elif key == "section":
                var.set("A")
            elif key == "gender":
                var.set("Male")
            else:
                var.set("")

    def _save_student(self):
        roll_no = self.inputs["roll_no"].get().strip()
        name = self.inputs["name"].get().strip()
        cls = self.inputs["class"].get().strip()
        sec = self.inputs["section"].get().strip()
        dob = self.inputs["dob"].get().strip()
        gender = self.inputs["gender"].get().strip()
        phone = self.inputs["phone"].get().strip()
        email = self.inputs["email"].get().strip()

        # Validations
        if not roll_no or not name or not cls or not sec:
            messagebox.showwarning("Validation Error", "Please fill in all mandatory fields (*).")
            return

        if not roll_no.isalnum():
            messagebox.showwarning("Validation Error", "Roll Number should be alphanumeric (e.g. 101 or S101).")
            return

        if phone and (not phone.isdigit() or len(phone) < 7):
            messagebox.showwarning("Validation Error", "Please enter a valid phone number.")
            return

        student_data = {
            "roll_no": roll_no,
            "name": name,
            "class": cls,
            "section": sec,
            "dob": dob,
            "gender": gender,
            "phone": phone,
            "email": email
        }

        success, msg = database.add_student(student_data)
        if success:
            messagebox.showinfo("Success", msg)
            self._clear_form()
        else:
            messagebox.showerror("Error", msg)
