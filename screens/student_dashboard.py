"""
screens/student_dashboard.py
-----------------------------
Dashboard for Student role — shows own profile, marks, result.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import database
import ui_styles

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


class StudentDashboard(ttk.Frame):
    def __init__(self, parent, logout_callback, user_info):
        super().__init__(parent)
        self.logout_callback = logout_callback
        self.user_info = user_info          # dict from database._USERS
        self.roll_no = user_info.get("roll_no", "")

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

        ttk.Label(top, text="Student Portal",
                  style="CardMuted.TLabel").pack(side="left", padx=12)

        ttk.Button(top, text="🚪 Logout",
                   style="Danger.TButton",
                   command=self.logout_callback).pack(side="right")

        # Scrollable body
        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        canvas = tk.Canvas(body, bg=ui_styles.COLOR_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        inner = ttk.Frame(canvas, padding=5)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1*(e.delta/120)), "units"))

        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        self._build_profile_card(inner)
        self._build_marks_card(inner)
        self._build_result_card(inner)

    def _section(self, parent, title, row, col=0, colspan=2):
        f = ttk.Frame(parent, style="Card.TFrame", padding=20)
        f.grid(row=row, column=col, columnspan=colspan,
               sticky="nsew", padx=8, pady=8)
        ttk.Label(f, text=title,
                  font=ui_styles.FONT_SUBTITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").pack(anchor="w", pady=(0, 12))
        return f

    def _row(self, parent, label, value, row):
        ttk.Label(parent, text=label,
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").grid(
            row=row, column=0, sticky="w", padx=(0, 20), pady=4)
        ttk.Label(parent, text=str(value),
                  style="CardMuted.TLabel").grid(
            row=row, column=1, sticky="w", pady=4)

    # ── Profile ──────────────────────────────────────────────────────
    def _build_profile_card(self, parent):
        card = self._section(parent, "👤 My Profile", row=0, col=0, colspan=1)
        grid = ttk.Frame(card, style="Card.TFrame")
        grid.pack(fill="x")

        student = database.get_student_by_roll(self.roll_no)
        if not student:
            ttk.Label(card, text="Student record not found.",
                      style="CardMuted.TLabel").pack()
            return

        fields = [
            ("Name",        student.get("name", "-")),
            ("Roll Number", student.get("roll_no", "-")),
            ("Class",       student.get("class", "-")),
            ("Section",     student.get("section", "-")),
            ("Gender",      student.get("gender", "-")),
            ("Date of Birth", student.get("dob", "-")),
            ("Phone",       student.get("phone", "-")),
            ("Email",       student.get("email", "-")),
        ]
        for i, (lbl, val) in enumerate(fields):
            self._row(grid, lbl, val, i)

    # ── Marks ────────────────────────────────────────────────────────
    def _build_marks_card(self, parent):
        card = self._section(parent, "📊 My Marks", row=0, col=1, colspan=1)

        marks = database.get_marks(self.roll_no)
        if not marks:
            ttk.Label(card, text="Marks not entered yet.",
                      style="CardMuted.TLabel").pack()
            return

        subjects = [
            ("Physics",              marks.get("physics",   0)),
            ("Chemistry",            marks.get("chemistry", 0)),
            ("Mathematics",          marks.get("maths",     0)),
            ("English",              marks.get("english",   0)),
            ("Computer Science / IP",marks.get("cs_ip",     0)),
        ]

        grid = ttk.Frame(card, style="Card.TFrame")
        grid.pack(fill="x")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=0)
        grid.columnconfigure(2, weight=0)

        ttk.Label(grid, text="Subject",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(grid, text="Marks",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").grid(row=0, column=1, sticky="w",
                                            padx=(20, 10), pady=4)
        ttk.Label(grid, text="Status",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").grid(row=0, column=2, sticky="w",
                                            padx=(10, 0), pady=4)

        for i, (sub, score) in enumerate(subjects, start=1):
            ttk.Label(grid, text=sub,
                      style="Card.TLabel").grid(
                row=i, column=0, sticky="w", pady=3)
            ttk.Label(grid, text=str(score),
                      style="Card.TLabel").grid(
                row=i, column=1, sticky="w", padx=(20, 10), pady=3)
            status_lbl = ttk.Label(grid,
                                   text="Pass" if score >= 33 else "Fail",
                                   foreground=(ui_styles.COLOR_SUCCESS
                                               if score >= 33
                                               else ui_styles.COLOR_DANGER),
                                   style="Card.TLabel")
            status_lbl.grid(row=i, column=2, sticky="w",
                            padx=(10, 0), pady=3)

    # ── Result Summary ───────────────────────────────────────────────
    def _build_result_card(self, parent):
        card = self._section(parent, "📋 My Result", row=1, col=0, colspan=2)

        result = database.get_result(self.roll_no)
        if not result or not result.get("has_marks"):
            ttk.Label(card, text="Result not available yet.",
                      style="CardMuted.TLabel").pack()
            return

        row_frame = ttk.Frame(card, style="Card.TFrame")
        row_frame.pack(fill="x")

        summary = [
            ("Total Marks",  f"{result['total']} / {result['max_total']}"),
            ("Percentage",   f"{result['percentage']}%"),
            ("Grade",        result["grade"]),
            ("Result Status",result["status"]),
        ]

        for i, (lbl, val) in enumerate(summary):
            ttk.Label(row_frame, text=lbl,
                      font=ui_styles.FONT_BODY_BOLD,
                      style="Card.TLabel").grid(
                row=i, column=0, sticky="w", padx=(0, 30), pady=5)

            color = ui_styles.COLOR_TEXT_MAIN
            if lbl == "Result Status":
                color = (ui_styles.COLOR_SUCCESS if "PASSED" in val
                         else ui_styles.COLOR_DANGER if "FAILED" in val
                         else ui_styles.COLOR_WARNING)

            ttk.Label(row_frame, text=val,
                      foreground=color,
                      font=(ui_styles.FONT_BODY_BOLD
                            if lbl == "Result Status"
                            else ui_styles.FONT_BODY),
                      style="Card.TLabel").grid(
                row=i, column=1, sticky="w", pady=5)

        ttk.Button(card, text="📄 Export Result as PDF",
                   style="Success.TButton",
                   command=self._export_pdf).pack(anchor="w", pady=(18, 0))

    # ── PDF Export ───────────────────────────────────────────────────
    def _export_pdf(self):
        result  = database.get_result(self.roll_no)
        student = database.get_student_by_roll(self.roll_no)
        if not result or not result.get("has_marks"):
            messagebox.showinfo("Info", "No marks available to export.")
            return

        default = (f"Result_{student.get('roll_no')}_"
                   f"{student.get('name','').replace(' ','_')}.pdf")
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf")],
            initialfile=default, title="Save Result PDF")
        if not path:
            return
        try:
            _build_result_pdf(path, result, student)
            messagebox.showinfo("Saved", f"PDF saved!\n{path}")
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_data(self):
        pass   # rebuild if needed


# ── Shared PDF builder (reused by ResultViewScreen too) ──────────────────────
def _build_result_pdf(filepath, result, student):
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
    sc     = (colors.HexColor("#10B981") if "PASSED" in status
              else colors.HexColor("#EF4444") if "FAILED" in status
              else colors.HexColor("#F59E0B"))

    el = []
    el.append(Paragraph("Student Management System", title_s))
    el.append(Paragraph("Academic Result Report Card", sub_s))
    el.append(Spacer(1, 0.3*cm))
    el.append(HRFlowable(width="100%", thickness=2,
                         color=colors.HexColor("#1E3A8A")))
    el.append(Spacer(1, 0.4*cm))

    el.append(Paragraph("Student Information", sec_s))
    info = [
        ["Student Name", student.get("name","-"),
         "Roll Number",  student.get("roll_no","-")],
        ["Class",        student.get("class","-"),
         "Section",      student.get("section","-")],
        ["Gender",       student.get("gender","-"),
         "Date of Birth",student.get("dob","-")],
    ]
    it = Table(info, colWidths=[4*cm,6*cm,4*cm,4*cm])
    it.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F8FAFC")),
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#E2E8F0")),
        ("BACKGROUND",(2,0),(2,-1),colors.HexColor("#E2E8F0")),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("PADDING",(0,0),(-1,-1),8),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E1")),
    ]))
    el.append(it); el.append(Spacer(1,0.5*cm))

    el.append(Paragraph("Subject-Wise Marks", sec_s))
    sd = [["Subject","Marks","Max","Status"]]
    rows = [("Physics","physics"),("Chemistry","chemistry"),
            ("Mathematics","maths"),("English","english"),
            ("Computer Science / IP","cs_ip")]
    for n,k in rows:
        sc2 = marks.get(k,0)
        sd.append([n, str(sc2), "100", "Pass" if sc2>=33 else "Fail"])
    mt = Table(sd, colWidths=[7*cm,4*cm,4*cm,3*cm])
    mt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ("PADDING",(0,0),(-1,-1),8),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(1,0),(-1,-1),
         [colors.HexColor("#FFFFFF"),colors.HexColor("#F8FAFC")]),
    ]))
    for ri,(n,k) in enumerate(rows,1):
        if marks.get(k,0)<33:
            mt.setStyle(TableStyle([
                ("TEXTCOLOR",(3,ri),(3,ri),colors.HexColor("#EF4444")),
                ("FONTNAME",(3,ri),(3,ri),"Helvetica-Bold"),
            ]))
    el.append(mt); el.append(Spacer(1,0.5*cm))

    el.append(Paragraph("Result Summary", sec_s))
    sm = [
        ["Total Marks",  f"{result.get('total',0)} / {result.get('max_total',500)}"],
        ["Percentage",   f"{result.get('percentage',0)}%"],
        ["Grade",        result.get("grade","-")],
        ["Result Status",status],
    ]
    st = Table(sm, colWidths=[7*cm,11*cm])
    st.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#E2E8F0")),
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),11),
        ("PADDING",(0,0),(-1,-1),10),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#CBD5E1")),
        ("TEXTCOLOR",(1,3),(1,3),sc),
        ("FONTNAME",(1,3),(1,3),"Helvetica-Bold"),
        ("FONTSIZE",(1,3),(1,3),13),
    ]))
    el.append(st)
    el.append(Spacer(1,0.8*cm))
    el.append(HRFlowable(width="100%",thickness=1,
                         color=colors.HexColor("#CBD5E1")))
    el.append(Spacer(1,0.3*cm))
    el.append(Paragraph(
        "Generated by Student Management System • Made by building_void",
        foot_s))
    doc.build(el)
