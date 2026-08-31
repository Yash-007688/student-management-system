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

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


class ResultViewScreen(ttk.Frame):
    def __init__(self, parent, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback
        self.loaded_roll = None
        self._last_result = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        # ── Top Bar ──────────────────────────────────────────────────
        top_bar = ttk.Frame(self, style="Card.TFrame", padding=(20, 12))
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        ttk.Button(top_bar, text="← Back to Dashboard",
                   style="Secondary.TButton",
                   command=self.on_back_callback).pack(side="left")

        ttk.Label(top_bar, text="Student Result / Report Card",
                  font=ui_styles.FONT_TITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").pack(side="left", padx=20)

        # ── Scrollable Body ──────────────────────────────────────────
        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        # Fetch row (not scrolled)
        fetch_card = ttk.Frame(body, style="Card.TFrame", padding=20)
        fetch_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(fetch_card, text="Enter Roll Number:",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").pack(side="left", padx=(0, 10))

        self.fetch_roll_var = tk.StringVar()
        fe = ttk.Entry(fetch_card, textvariable=self.fetch_roll_var, width=20)
        fe.pack(side="left", padx=(0, 15))
        fe.bind("<Return>", lambda e: self._fetch_result())

        ttk.Button(fetch_card, text="📋 Get Result",
                   style="Primary.TButton",
                   command=self._fetch_result).pack(side="left")

        # Canvas + scrollbar for the result card
        canvas_frame = ttk.Frame(body)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, bg=ui_styles.COLOR_CARD_BG,
                                highlightthickness=0)
        vsb = ttk.Scrollbar(canvas_frame, orient="vertical",
                            command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # Inner frame inside canvas
        self.inner = ttk.Frame(self.canvas, style="Card.TFrame", padding=25)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw")

        # Resize inner frame when canvas width changes
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.inner.bind("<Configure>", self._on_inner_resize)

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self._build_result_card()

    # ── Canvas resize helpers ────────────────────────────────────────
    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_inner_resize(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Result card content ──────────────────────────────────────────
    def _build_result_card(self):
        f = self.inner

        ttk.Label(f, text="Result Report",
                  font=ui_styles.FONT_SUBTITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Student info
        self.result_labels = {}
        for i, (ltext, key) in enumerate([
            ("Student Name", "name"), ("Roll Number", "roll_no"),
            ("Class", "class"),      ("Section", "section"),
            ("Gender", "gender"),    ("Date of Birth", "dob"),
        ]):
            ttk.Label(f, text=ltext, font=ui_styles.FONT_BODY_BOLD,
                      style="Card.TLabel").grid(
                row=i+1, column=0, sticky="w", padx=(10, 10), pady=(6, 2))
            lbl = ttk.Label(f, text="-", style="CardMuted.TLabel")
            lbl.grid(row=i+1, column=1, sticky="w", padx=(10, 10), pady=(6, 2))
            self.result_labels[key] = lbl

        # Subject marks header
        ttk.Label(f, text="Subject Marks",
                  font=ui_styles.FONT_HEADING,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").grid(
            row=10, column=0, columnspan=2, sticky="w", pady=(15, 10))

        self.subject_labels = {}
        for i, (ltext, key) in enumerate([
            ("Physics", "physics"), ("Chemistry", "chemistry"),
            ("Mathematics", "maths"), ("English", "english"),
            ("Computer Science / IP", "cs_ip"),
        ]):
            ttk.Label(f, text=ltext, font=ui_styles.FONT_BODY,
                      style="Card.TLabel").grid(
                row=i+11, column=0, sticky="w", padx=(10, 10), pady=(4, 2))
            lbl = ttk.Label(f, text="-", style="CardMuted.TLabel")
            lbl.grid(row=i+11, column=1, sticky="w", padx=(10, 10), pady=(4, 2))
            self.subject_labels[key] = lbl

        # Summary header
        ttk.Label(f, text="Summary",
                  font=ui_styles.FONT_HEADING,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").grid(
            row=20, column=0, columnspan=2, sticky="w", pady=(15, 10))

        self.summary_labels = {}
        for i, (ltext, key) in enumerate([
            ("Total Marks", "total"), ("Maximum Marks", "max_total"),
            ("Percentage (%)", "percentage"), ("Grade", "grade"),
            ("Result Status", "status"),
        ]):
            ttk.Label(f, text=ltext, font=ui_styles.FONT_BODY_BOLD,
                      style="Card.TLabel").grid(
                row=i+21, column=0, sticky="w", padx=(10, 10), pady=(6, 2))
            lbl = ttk.Label(f, text="-", style="CardMuted.TLabel")
            lbl.grid(row=i+21, column=1, sticky="w", padx=(10, 10), pady=(6, 2))
            self.summary_labels[key] = lbl

        # ── Export Button (always visible inside scroll) ─────────────
        btn_frame = ttk.Frame(f, style="Card.TFrame")
        btn_frame.grid(row=30, column=0, columnspan=2,
                       sticky="w", pady=(25, 10))

        ttk.Button(btn_frame, text="📄 Export Result as PDF",
                   style="Success.TButton",
                   command=self._export_pdf).pack(side="left", padx=(0, 15))

        self.status_lbl = ttk.Label(btn_frame,
                                    text="Fetch a student to view result.",
                                    style="CardMuted.TLabel")
        self.status_lbl.pack(side="left")

    # ── Fetch & display result ───────────────────────────────────────
    def _fetch_result(self):
        roll = self.fetch_roll_var.get().strip()
        if not roll:
            messagebox.showwarning("Input Needed", "Please enter a Roll Number.")
            return

        result = database.get_result(roll)
        if not result:
            messagebox.showerror("Not Found",
                                 f"No student found with Roll Number '{roll}'.")
            self._clear_display()
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
            self.summary_labels["percentage"].configure(
                text=str(result.get("percentage", "-")) + "%")
            self.summary_labels["grade"].configure(text=result.get("grade", "-"))

            status = result.get("status", "-")
            self.summary_labels["status"].configure(text=status)
            if "PASSED" in status:
                self.summary_labels["status"].configure(
                    foreground=ui_styles.COLOR_SUCCESS)
            elif "FAILED" in status:
                self.summary_labels["status"].configure(
                    foreground=ui_styles.COLOR_DANGER)
            elif "COMPARTMENT" in status:
                self.summary_labels["status"].configure(
                    foreground=ui_styles.COLOR_WARNING)

            self.status_lbl.configure(
                text=f"Result loaded for: {student.get('name')}")
        else:
            for lbl in self.subject_labels.values():
                lbl.configure(text="-")
            for k in ("total", "max_total", "percentage", "grade", "status"):
                self.summary_labels[k].configure(
                    text="-", foreground=ui_styles.COLOR_TEXT_MUTED)
            self.status_lbl.configure(
                text="Marks not entered yet for this student.")

        # Scroll to top after loading
        self.canvas.yview_moveto(0)

    def _clear_display(self):
        for lbl in self.result_labels.values():
            lbl.configure(text="-")
        for lbl in self.subject_labels.values():
            lbl.configure(text="-")
        for lbl in self.summary_labels.values():
            lbl.configure(text="-", foreground=ui_styles.COLOR_TEXT_MUTED)
        self.loaded_roll = None
        self._last_result = None
        self.status_lbl.configure(text="Fetch a student to view result.")

    # ── PDF Export ───────────────────────────────────────────────────
    def _export_pdf(self):
        if not self.loaded_roll or not self._last_result:
            messagebox.showinfo("Info", "Please fetch a student result first.")
            return

        result = self._last_result
        student = result.get("student", {})

        if not result.get("has_marks"):
            messagebox.showwarning("No Marks",
                                   "Marks not entered yet. Cannot generate PDF.")
            return

        default_name = (f"Result_{student.get('roll_no', 'student')}_"
                        f"{student.get('name', '').replace(' ', '_')}.pdf")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=default_name,
            title="Save Result PDF"
        )
        if not filepath:
            return

        try:
            self._generate_pdf(filepath, result, student)
            messagebox.showinfo("Success", f"PDF saved!\n{filepath}")
            os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("PDF Error", f"Could not generate PDF:\n{e}")

    def _generate_pdf(self, filepath, result, student):
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        title_s = ParagraphStyle("t", parent=styles["Title"], fontSize=20,
                                 textColor=colors.HexColor("#1E3A8A"),
                                 spaceAfter=4, alignment=TA_CENTER)
        sub_s   = ParagraphStyle("s", parent=styles["Normal"], fontSize=11,
                                 textColor=colors.HexColor("#64748B"),
                                 spaceAfter=2, alignment=TA_CENTER)
        sec_s   = ParagraphStyle("h", parent=styles["Normal"], fontSize=12,
                                 textColor=colors.HexColor("#1E3A8A"),
                                 fontName="Helvetica-Bold",
                                 spaceBefore=12, spaceAfter=6)
        foot_s  = ParagraphStyle("f", parent=styles["Normal"], fontSize=8,
                                 textColor=colors.HexColor("#94A3B8"),
                                 alignment=TA_CENTER)

        marks  = result.get("marks", {})
        status = result.get("status", "-")
        status_color = (colors.HexColor("#10B981") if "PASSED" in status
                        else colors.HexColor("#EF4444") if "FAILED" in status
                        else colors.HexColor("#F59E0B"))

        el = []

        # Header
        el.append(Paragraph("Student Management System", title_s))
        el.append(Paragraph("Academic Result Report Card — Class 12", sub_s))
        el.append(Spacer(1, 0.3*cm))
        el.append(HRFlowable(width="100%", thickness=2,
                             color=colors.HexColor("#1E3A8A")))
        el.append(Spacer(1, 0.4*cm))

        # Student info
        el.append(Paragraph("Student Information", sec_s))
        info = [
            ["Student Name", student.get("name", "-"),
             "Roll Number",  student.get("roll_no", "-")],
            ["Class",        student.get("class", "-"),
             "Section",      student.get("section", "-")],
            ["Gender",       student.get("gender", "-"),
             "Date of Birth",student.get("dob", "-")],
        ]
        it = Table(info, colWidths=[4*cm, 6*cm, 4*cm, 4*cm])
        it.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#E2E8F0")),
            ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTNAME",   (2,0), (2,-1), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 10),
            ("PADDING",    (0,0), (-1,-1), 8),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        el.append(it)
        el.append(Spacer(1, 0.5*cm))

        # Subject marks
        el.append(Paragraph("Subject-Wise Marks", sec_s))
        sub_data = [["Subject", "Marks Obtained", "Max Marks", "Status"]]
        rows = [("Physics","physics"),("Chemistry","chemistry"),
                ("Mathematics","maths"),("English","english"),
                ("Computer Science / IP","cs_ip")]
        for name, key in rows:
            sc = marks.get(key, 0)
            sub_data.append([name, str(sc), "100",
                             "Pass" if sc >= 33 else "Fail"])

        mt = Table(sub_data, colWidths=[7*cm, 4*cm, 4*cm, 3*cm])
        mt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 10),
            ("ALIGN",      (1,0), (-1,-1), "CENTER"),
            ("PADDING",    (0,0), (-1,-1), 8),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ("ROWBACKGROUNDS", (1,0), (-1,-1),
             [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ]))
        for ri, (name, key) in enumerate(rows, start=1):
            if marks.get(key, 0) < 33:
                mt.setStyle(TableStyle([
                    ("TEXTCOLOR", (3,ri),(3,ri), colors.HexColor("#EF4444")),
                    ("FONTNAME",  (3,ri),(3,ri), "Helvetica-Bold"),
                ]))
        el.append(mt)
        el.append(Spacer(1, 0.5*cm))

        # Summary
        el.append(Paragraph("Result Summary", sec_s))
        sm = [
            ["Total Marks",   f"{result.get('total',0)} / {result.get('max_total',500)}"],
            ["Percentage",    f"{result.get('percentage',0)}%"],
            ["Grade",         result.get("grade", "-")],
            ["Result Status", status],
        ]
        st = Table(sm, colWidths=[7*cm, 11*cm])
        st.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(0,-1), colors.HexColor("#E2E8F0")),
            ("FONTNAME",   (0,0),(0,-1), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0),(-1,-1), 11),
            ("PADDING",    (0,0),(-1,-1), 10),
            ("GRID",       (0,0),(-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ("TEXTCOLOR",  (1,3),(1,3),  status_color),
            ("FONTNAME",   (1,3),(1,3),  "Helvetica-Bold"),
            ("FONTSIZE",   (1,3),(1,3),  13),
        ]))
        el.append(st)

        el.append(Spacer(1, 0.8*cm))
        el.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#CBD5E1")))
        el.append(Spacer(1, 0.3*cm))
        el.append(Paragraph(
            "Generated by Student Management System • Made by building_void",
            foot_s))

        doc.build(el)
