"""
screens/result_view.py
----------------------
Screen to view student results including percentage, grade, and pass/fail status.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class ResultViewScreen(ttk.Frame):
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
            text="Student Result / Report Card",
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
        fetch_entry.bind("<Return>", lambda e: self._fetch_result())

        fetch_btn = ttk.Button(
            fetch_card,
            text="📋 Get Result",
            style="Primary.TButton",
            command=self._fetch_result
        )
        fetch_btn.pack(side="left")

        # Result Display Card
        self.result_card = ttk.Frame(content_frame, style="Card.TFrame", padding=25)
        self.result_card.pack(fill="both", expand=True)

        ttk.Label(
            self.result_card,
            text="Result Report",
            font=ui_styles.FONT_SUBTITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Result fields (read-only)
        self.result_labels = {}

        fields = [
            ("Student Name", "name"),
            ("Roll Number", "roll_no"),
            ("Class", "class"),
            ("Section", "section"),
            ("Gender", "gender"),
            ("Date of Birth", "dob"),
        ]

        for i, (label_text, key) in enumerate(fields):
            row_idx = i + 1

            ttk.Label(self.result_card, text=label_text, font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").grid(
                row=row_idx, column=0, sticky="w", padx=(10, 10), pady=(6, 2)
            )
            val_label = ttk.Label(self.result_card, text="-", style="CardMuted.TLabel")
            val_label.grid(row=row_idx, column=1, sticky="w", padx=(10, 10), pady=(6, 2))
            self.result_labels[key] = val_label

        # Marks section header
        ttk.Label(
            self.result_card,
            text="Subject Marks",
            font=ui_styles.FONT_HEADING,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(15, 10))

        self.subject_labels = {}
        subjects = [
            ("Physics", "physics"),
            ("Chemistry", "chemistry"),
            ("Mathematics", "maths"),
            ("English", "english"),
            ("Computer Science / IP", "cs_ip"),
        ]

        for i, (label_text, key) in enumerate(subjects):
            row_idx = i + 11

            ttk.Label(self.result_card, text=label_text, font=ui_styles.FONT_BODY, style="Card.TLabel").grid(
                row=row_idx, column=0, sticky="w", padx=(10, 10), pady=(4, 2)
            )
            val_label = ttk.Label(self.result_card, text="-", style="CardMuted.TLabel")
            val_label.grid(row=row_idx, column=1, sticky="w", padx=(10, 10), pady=(4, 2))
            self.subject_labels[key] = val_label

        # Summary section
        ttk.Label(
            self.result_card,
            text="Summary",
            font=ui_styles.FONT_HEADING,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=20, column=0, columnspan=2, sticky="w", pady=(15, 10))

        summary_fields = [
            ("Total Marks", "total"),
            ("Maximum Marks", "max_total"),
            ("Percentage (%)", "percentage"),
            ("Grade", "grade"),
            ("Result Status", "status"),
        ]

        self.summary_labels = {}

        for i, (label_text, key) in enumerate(summary_fields):
            row_idx = i + 21

            ttk.Label(self.result_card, text=label_text, font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").grid(
                row=row_idx, column=0, sticky="w", padx=(10, 10), pady=(6, 2)
            )

            if key == "status":
                # Status label with color coding
                val_label = ttk.Label(self.result_card, text="-", style="CardMuted.TLabel", foreground=ui_styles.COLOR_TEXT_MUTED)
            else:
                val_label = ttk.Label(self.result_card, text="-", style="CardMuted.TLabel")
            val_label.grid(row=row_idx, column=1, sticky="w", padx=(10, 10), pady=(6, 2))
            self.summary_labels[key] = val_label

        # Print button (placeholder for printing/report generation)
        btn_frame = ttk.Frame(self.result_card, style="Card.TFrame")
        btn_frame.grid(row=30, column=0, columnspan=2, sticky="w", pady=(20, 0))

        print_btn = ttk.Button(
            btn_frame,
            text="📄 Print Report",
            style="Secondary.TButton",
            command=self._print_report
        )
        print_btn.pack(side="left", padx=(0, 10))

        self.status_lbl = ttk.Label(btn_frame, text="Fetch a student to view result.", style="CardMuted.TLabel")
        self.status_lbl.pack(side="left", padx=10)

    def _fetch_result(self):
        roll = self.fetch_roll_var.get().strip()
        if not roll:
            messagebox.showwarning("Input Needed", "Please enter a Roll Number to view result.")
            return

        result = database.get_result(roll)
        if not result:
            messagebox.showerror("Not Found", f"No student found with Roll Number '{roll}'.")
            self._clear_result_display()
            self.status_lbl.configure(text="No result found.")
            return

        self.loaded_roll = roll

        # Fill student info
        student = result.get("student", {})
        self.result_labels["name"].configure(text=student.get("name", "-"))
        self.result_labels["roll_no"].configure(text=student.get("roll_no", "-"))
        self.result_labels["class"].configure(text=student.get("class", "-"))
        self.result_labels["section"].configure(text=student.get("section", "-"))
        self.result_labels["gender"].configure(text=student.get("gender", "-"))
        self.result_labels["dob"].configure(text=student.get("dob", "-"))

        # Fill marks
        if result.get("has_marks"):
            marks = result.get("marks", {})
            self.subject_labels["physics"].configure(text=str(marks.get("physics", "-")))
            self.subject_labels["chemistry"].configure(text=str(marks.get("chemistry", "-")))
            self.subject_labels["maths"].configure(text=str(marks.get("maths", "-")))
            self.subject_labels["english"].configure(text=str(marks.get("english", "-")))
            self.subject_labels["cs_ip"].configure(text=str(marks.get("cs_ip", "-")))

            # Fill summary
            self.summary_labels["total"].configure(text=str(result.get("total", "-")))
            self.summary_labels["max_total"].configure(text=str(result.get("max_total", "-")))
            self.summary_labels["percentage"].configure(text=str(result.get("percentage", "-")) + "%")
            self.summary_labels["grade"].configure(text=result.get("grade", "-"))

            # Color code the status
            status = result.get("status", "-")
            self.summary_labels["status"].configure(text=status)
            if "PASSED" in status:
                self.summary_labels["status"].configure(foreground=ui_styles.COLOR_SUCCESS)
            elif "FAILED" in status:
                self.summary_labels["status"].configure(foreground=ui_styles.COLOR_DANGER)
            elif "COMPARTMENT" in status:
                self.summary_labels["status"].configure(foreground=ui_styles.COLOR_WARNING)
            else:
                self.summary_labels["status"].configure(foreground=ui_styles.COLOR_TEXT_MUTED)

            self.status_lbl.configure(text=f"Result generated for: {student.get('name')}")
        else:
            self._clear_marks_display()
            self.summary_labels["total"].configure(text="-")
            self.summary_labels["percentage"].configure(text="-")
            self.summary_labels["grade"].configure(text="-")
            self.summary_labels["status"].configure(text="-", foreground=ui_styles.COLOR_TEXT_MUTED)
            self.status_lbl.configure(text="Student exists but marks not entered yet.")

    def _clear_result_display(self):
        for label in self.result_labels.values():
            label.configure(text="-")
        self._clear_marks_display()
        self.summary_labels["total"].configure(text="-")
        self.summary_labels["percentage"].configure(text="-")
        self.summary_labels["grade"].configure(text="-")
        self.summary_labels["status"].configure(text="-", foreground=ui_styles.COLOR_TEXT_MUTED)
        self.loaded_roll = None

    def _clear_marks_display(self):
        for label in self.subject_labels.values():
            label.configure(text="-")

    def _print_report(self):
        if not self.loaded_roll:
            messagebox.showinfo("Info", "Please fetch a student result first.")
            return

        # Simple print simulation
        report = f"""
STUDENT RESULT REPORT
=====================
Roll Number: {self.result_labels['roll_no'].cget('text')}
Name: {self.result_labels['name'].cget('text')}
Class: {self.result_labels['class'].cget('text')} - {self.result_labels['section'].cget('text')}

SUBJECT MARKS:
Physics: {self.subject_labels['physics'].cget('text')}
Chemistry: {self.subject_labels['chemistry'].cget('text')}
Mathematics: {self.subject_labels['maths'].cget('text')}
English: {self.subject_labels['english'].cget('text')}
CS/IP: {self.subject_labels['cs_ip'].cget('text')}

SUMMARY:
Total: {self.summary_labels['total'].cget('text')}
Percentage: {self.summary_labels['percentage'].cget('text')}
Grade: {self.summary_labels['grade'].cget('text')}
Status: {self.summary_labels['status'].cget('text')}
"""
        print(report)
        messagebox.showinfo("Print Report", "Report printed to console/terminal.")
