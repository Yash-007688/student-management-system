"""
screens/result_view.py
----------------------
Screen to view student results including percentage, grade, and pass/fail status.
Includes Export to PDF feature using reportlab.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import database
import ui_styles

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class ResultViewScreen(ttk.Frame):
    def __init__(self, parent, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback
        self.loaded_roll = None
        self._last_result = None   # stores full result dict for PDF export

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        # 1. Top Bar
        top_bar = ttk.Frame(self, style="Card.TFrame", padding=(20, 12))
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        ttk.Button(
            top_bar, text="← Back to Dashboard",
            style="Secondary.TButton", command=self.on_back_callback
        ).pack(side="left")

        ttk.Label(
            top_bar, text="Student Result / Report Card",
            font=ui_styles.FONT_TITLE, foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).pack(side="left", padx=20)

        # 2. Main Content
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)

        # Fetch Card
        fetch_card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        fetch_card.pack(fill="x", pady=(0, 15))

        ttk.Label(fetch_card, text="Enter Roll Number:", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(side="left", padx=(0, 10))
        self.fetch_roll_var = tk.StringVar()
        fetch_entry = ttk.Entry(fetch_card, textvariable=self.fetch_roll_var, width=20)
        fetch_entry.pack(side="left", padx=(0, 15))
        fetch_entry.bind("<Return>", lambda e: self._fetch_result())

        ttk.Button(
            fetch_card, text="📋 Get Result",
            style="Primary.TButton", command=self._fetch_result
        ).pack(side="left")

        # Result Display Card
        self.result_card = ttk.Frame(content_frame, style="Card.TFrame", padding=25)
        self.result_card.pack(fill="both", expand=True)

        ttk.Label(
            self.result_card, text="Result Report",
            font=ui_styles.FONT_SUBTITLE, foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Student info labels
        self.result_labels = {}
        for i, (label_text, key) in enumerate([
            ("Student Name", "name"), ("Roll Number", "roll_no"),
            ("Class", "class"), ("Section", "section"),
            ("Gender", "gender"), ("Date of Birth", "dob"),
        ]):
            ttk.Label(self.result_card, text=label_text, font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").grid(
                row=i+1, column=0, sticky="w", padx=(10,10), pady=(6,2))
            lbl = ttk.Label(self.result_card, text="-", style="CardMuted.TLabel")
            lbl.grid(row=i+1, column=1, sticky="w", padx=(10,10), pady=(6,2))
            self.result_labels[key] = lbl

        # Subject marks
        ttk.Label(
            self.result_card, text="Subject Marks",
            font=ui_styles.FONT_HEADING, foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(15, 10))

        self.subject_labels = {}
        for i, (label_text, key) in enumerate([
            ("Physics", "physics"), ("Chemistry", "chemistry"),
            ("Mathematics", "maths"), ("English", "english"),
            ("Computer Science / IP", "cs_ip"),
        ]):
            ttk.Label(self.result_card, text=label_text, font=ui_styles.FONT_BODY, style="Card.TLabel").grid(
                row=i+11, column=0, sticky="w", padx=(10,10), pady=(4,2))
            lbl = ttk.Label(self.result_card, text="-", style="CardMuted.TLabel")
            lbl.grid(row=i+11, column=1, sticky="w", padx=(10,10), pady=(4,2))
            self.subject_labels[key] = lbl

        # Summary
        ttk.Label(
            self.result_card, text="Summary",
            font=ui_styles.FONT_HEADING, foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).grid(row=20, column=0, columnspan=2, sticky="w", pady=(15, 10))

        self.summary_labels = {}
        for i, (label_text, key) in enumerate([
            ("Total Marks", "total"), ("Maximum Marks", "max_total"),
            ("Percentage (%)", "percentage"), ("Grade", "grade"),
            ("Result Status", "status"),
        ]):
            ttk.Label(self.result_card, text=label_text, font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").grid(
                row=i+21, column=0, sticky="w", padx=(10,10), pady=(6,2))
            lbl = ttk.Label(self.result_card, text="-", style="CardMuted.TLabel")
            lbl.grid(row=i+21, column=1, sticky="w", padx=(10,10), pady=(6,2))
            self.summary_labels[key] = lbl

        # Buttons Row
        btn_frame = ttk.Frame(self.result_card, style="Card.TFrame")
        btn_frame.grid(row=30, column=0, columnspan=2, sticky="w", pady=(20, 0))

        ttk.Button(
            btn_frame, text="📄 Export Result as PDF",
            style="Success.TButton", command=self._export_pdf
        ).pack(side="left", padx=(0, 10))

        self.status_lbl = ttk.Label(btn_frame, text="Fetch a student to view result.", style="CardMuted.TLabel")
        self.status_lbl.pack(side="left", padx=10)

    # ------------------------------------------------------------------
    def _fetch_result(self):
        roll = self.fetch_roll_var.get().strip()
        if not roll:
            messagebox.showwarning("Input Needed", "Please enter a Roll Number.")
            return

        result = database.get_result(roll)
        if not result:
            messagebox.showerror("Not Found", f"No student found with Roll Number '{roll}'.")
            self._clear_result_display()
            return

        self.loaded_roll = roll
        self._last_result = result
        student = result.get("student", {})

        self.result_labels["name"].configure(text=student.get("name", "-"))
        self.result_labels["roll_no"].configure(text=student.get("roll_no", "-"))
        self.result_labels["class"].configure(text=student.get("class", "-"))
        self.result_labels["section"].configure(text=student.get("section", "-"))
        self.result_labels["gender"].configure(text=student.get("gender", "-"))
        self.result_labels["dob"].configure(text=student.get("dob", "-"))

        if result.get("has_marks"):
            marks = result.get("marks", {})
            self.subject_labels["physics"].configure(text=str(marks.get("physics", "-")))
            self.subject_labels["chemistry"].configure(text=str(marks.get("chemistry", "-")))
            self.subject_labels["maths"].configure(text=str(marks.get("maths", "-")))
            self.subject_labels["english"].configure(text=str(marks.get("english", "-")))
            self.subject_labels["cs_ip"].configure(text=str(marks.get("cs_ip", "-")))

            self.summary_labels["total"].configure(text=str(result.get("total", "-")))
            self.summary_labels["max_total"].configure(text=str(result.get("max_total", "-")))
            self.summary_labels["percentage"].configure(text=str(result.get("percentage", "-")) + "%")
            self.summary_labels["grade"].configure(text=result.get("grade", "-"))

            status = result.get("status", "-")
            self.summary_labels["status"].configure(text=status)
            if "PASSED" in status:
                self.summary_labels["status"].configure(foreground=ui_styles.COLOR_SUCCESS)
            elif "FAILED" in status:
                self.summary_labels["status"].configure(foreground=ui_styles.COLOR_DANGER)
            elif "COMPARTMENT" in status:
                self.summary_labels["status"].configure(foreground=ui_styles.COLOR_WARNING)

            self.status_lbl.configure(text=f"Result loaded for: {student.get('name')}")
        else:
            self._clear_marks_display()
            for k in ("total", "max_total", "percentage", "grade"):
                self.summary_labels[k].configure(text="-")
            self.summary_labels["status"].configure(text="-", foreground=ui_styles.COLOR_TEXT_MUTED)
            self.status_lbl.configure(text="Marks not entered yet for this student.")

    # ------------------------------------------------------------------
    def _clear_result_display(self):
        for lbl in self.result_labels.values():
            lbl.configure(text="-")
        self._clear_marks_display()
        for lbl in self.summary_labels.values():
            lbl.configure(text="-", foreground=ui_styles.COLOR_TEXT_MUTED)
        self.loaded_roll = None
        self._last_result = None
        self.status_lbl.configure(text="Fetch a student to view result.")

    def _clear_marks_display(self):
        for lbl in self.subject_labels.values():
            lbl.configure(text="-")

    # ------------------------------------------------------------------
    def _export_pdf(self):
        if not self.loaded_roll or not self._last_result:
            messagebox.showinfo("Info", "Please fetch a student result first.")
            return

        result = self._last_result
        student = result.get("student", {})

        if not result.get("has_marks"):
            messagebox.showwarning("No Marks", "Marks are not entered yet. Cannot generate PDF.")
            return

        # Ask user where to save
        default_name = f"Result_{student.get('roll_no', 'student')}_{student.get('name', '').replace(' ', '_')}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=default_name,
            title="Save Result PDF"
        )
        if not filepath:
            return  # user cancelled

        try:
            self._generate_pdf(filepath, result, student)
            messagebox.showinfo("Success", f"PDF saved successfully!\n{filepath}")
            os.startfile(filepath)   # auto-open PDF on Windows
        except Exception as e:
            messagebox.showerror("PDF Error", f"Could not generate PDF:\n{e}")

    # ------------------------------------------------------------------
    def _generate_pdf(self, filepath, result, student):
        """Builds a clean A4 result card PDF using reportlab."""
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "title", parent=styles["Title"],
            fontSize=20, textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=4, alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            "subtitle", parent=styles["Normal"],
            fontSize=11, textColor=colors.HexColor("#64748B"),
            spaceAfter=2, alignment=TA_CENTER
        )
        section_style = ParagraphStyle(
            "section", parent=styles["Normal"],
            fontSize=12, textColor=colors.HexColor("#1E3A8A"),
            fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6
        )
        normal = styles["Normal"]

        marks = result.get("marks", {})
        status = result.get("status", "-")

        # Status color
        if "PASSED" in status:
            status_color = colors.HexColor("#10B981")
        elif "FAILED" in status:
            status_color = colors.HexColor("#EF4444")
        else:
            status_color = colors.HexColor("#F59E0B")

        elements = []

        # --- Header ---
        elements.append(Paragraph("🎓 Student Management System", title_style))
        elements.append(Paragraph("Academic Result Report Card — Class 12", subtitle_style))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1E3A8A")))
        elements.append(Spacer(1, 0.4*cm))

        # --- Student Info Table ---
        elements.append(Paragraph("Student Information", section_style))

        info_data = [
            ["Student Name", student.get("name", "-"), "Roll Number", student.get("roll_no", "-")],
            ["Class", student.get("class", "-"), "Section", student.get("section", "-")],
            ["Gender", student.get("gender", "-"), "Date of Birth", student.get("dob", "-")],
        ]

        info_table = Table(info_data, colWidths=[4*cm, 6*cm, 4*cm, 4*cm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#E2E8F0")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*cm))

        # --- Subject Marks Table ---
        elements.append(Paragraph("Subject-Wise Marks", section_style))

        subject_data = [["Subject", "Marks Obtained", "Maximum Marks", "Status"]]
        subject_map = [
            ("Physics", "physics"),
            ("Chemistry", "chemistry"),
            ("Mathematics", "maths"),
            ("English", "english"),
            ("Computer Science / IP", "cs_ip"),
        ]

        for sub_name, key in subject_map:
            score = marks.get(key, 0)
            sub_status = "Pass" if score >= 33 else "Fail"
            subject_data.append([sub_name, str(score), "100", sub_status])

        marks_table = Table(subject_data, colWidths=[7*cm, 4*cm, 4*cm, 3*cm])
        marks_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ]))

        # Color Fail cells red
        for row_idx, (sub_name, key) in enumerate(subject_map, start=1):
            score = marks.get(key, 0)
            if score < 33:
                marks_table.setStyle(TableStyle([
                    ("TEXTCOLOR", (3, row_idx), (3, row_idx), colors.HexColor("#EF4444")),
                    ("FONTNAME", (3, row_idx), (3, row_idx), "Helvetica-Bold"),
                ]))

        elements.append(marks_table)
        elements.append(Spacer(1, 0.5*cm))

        # --- Summary Table ---
        elements.append(Paragraph("Result Summary", section_style))

        summary_data = [
            ["Total Marks", f"{result.get('total', 0)} / {result.get('max_total', 500)}"],
            ["Percentage", f"{result.get('percentage', 0)}%"],
            ["Grade", result.get("grade", "-")],
            ["Result Status", status],
        ]

        summary_table = Table(summary_data, colWidths=[7*cm, 11*cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E2E8F0")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TEXTCOLOR", (1, 3), (1, 3), status_color),
            ("FONTNAME", (1, 3), (1, 3), "Helvetica-Bold"),
            ("FONTSIZE", (1, 3), (1, 3), 13),
        ]))
        elements.append(summary_table)

        elements.append(Spacer(1, 0.8*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1")))
        elements.append(Spacer(1, 0.3*cm))

        footer_style = ParagraphStyle(
            "footer", parent=normal,
            fontSize=8, textColor=colors.HexColor("#94A3B8"),
            alignment=TA_CENTER
        )
        elements.append(Paragraph("Generated by Student Management System • Made by building_void", footer_style))

        doc.build(elements)
