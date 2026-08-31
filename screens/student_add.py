"""
screens/student_add.py
----------------------
Screen to register a new student with input validation.
Clean 2-column layout with proper spacing and styled fields.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class AddStudentScreen(ttk.Frame):
    def __init__(self, parent, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback
        self.inputs = {}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    # ── helpers ──────────────────────────────────────────────────────
    def _make_label(self, parent, text, row, col):
        ttk.Label(parent, text=text,
                  font=ui_styles.FONT_BODY_BOLD,
                  foreground=ui_styles.COLOR_TEXT_MUTED,
                  style="Card.TLabel"
                  ).grid(row=row, column=col, sticky="w",
                         padx=(0, 20), pady=(0, 4))

    def _make_entry(self, parent, var, row, col, placeholder=""):
        e = ttk.Entry(parent, textvariable=var, font=ui_styles.FONT_BODY)
        e.grid(row=row, column=col, sticky="ew", padx=(0, 20), pady=(0, 18))
        if placeholder:
            e.insert(0, placeholder)
            e.configure(foreground=ui_styles.COLOR_TEXT_MUTED)
            e.bind("<FocusIn>",
                   lambda ev, w=e, ph=placeholder: self._on_focus_in(ev, w, ph))
            e.bind("<FocusOut>",
                   lambda ev, w=e, ph=placeholder, v=var:
                   self._on_focus_out(ev, w, ph, v))
        return e

    def _on_focus_in(self, event, widget, placeholder):
        if widget.get() == placeholder:
            widget.delete(0, "end")
            widget.configure(foreground=ui_styles.COLOR_TEXT_MAIN)

    def _on_focus_out(self, event, widget, placeholder, var):
        if not widget.get().strip():
            widget.delete(0, "end")
            widget.insert(0, placeholder)
            widget.configure(foreground=ui_styles.COLOR_TEXT_MUTED)
            var.set("")

    def _make_combo(self, parent, var, values, row, col, default=None):
        cb = ttk.Combobox(parent, textvariable=var, values=values,
                          state="readonly", font=ui_styles.FONT_BODY)
        cb.grid(row=row, column=col, sticky="ew", padx=(0, 20), pady=(0, 18))
        if default:
            cb.set(default)
        return cb

    # ── UI build ─────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        top_bar = ttk.Frame(self, style="Card.TFrame", padding=(20, 14))
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        ttk.Button(top_bar, text="← Back to Dashboard",
                   style="Secondary.TButton",
                   command=self.on_back_callback).pack(side="left")

        ttk.Label(top_bar, text="Add New Student",
                  font=ui_styles.FONT_TITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").pack(side="left", padx=20)

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

        inner = ttk.Frame(canvas, style="Card.TFrame", padding=30)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")

        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        inner.bind("<Configure>",
                   lambda e: canvas.configure(
                       scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1*(e.delta/120)), "units"))

        # ── Form title ───────────────────────────────────────────────
        ttk.Label(inner, text="Student Registration Form",
                  font=ui_styles.FONT_SUBTITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel"
                  ).grid(row=0, column=0, columnspan=4,
                         sticky="w", pady=(0, 6))

        ttk.Label(inner,
                  text="Fields marked with * are required",
                  font=ui_styles.FONT_SMALL,
                  foreground=ui_styles.COLOR_TEXT_MUTED,
                  style="Card.TLabel"
                  ).grid(row=1, column=0, columnspan=4,
                         sticky="w", pady=(0, 20))

        # column weights: label | field | label | field
        inner.columnconfigure(0, weight=0, minsize=160)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(2, weight=0, minsize=160)
        inner.columnconfigure(3, weight=1)

        # ── Row 1: Roll Number | Full Name ───────────────────────────
        self._make_label(inner, "Roll Number *", 2, 0)
        self._make_label(inner, "Full Name *",   2, 2)

        v_roll = tk.StringVar(); self.inputs["roll_no"] = v_roll
        v_name = tk.StringVar(); self.inputs["name"]    = v_name
        self._make_entry(inner, v_roll, 3, 0, "e.g. 101")
        self._make_entry(inner, v_name, 3, 2, "e.g. Rahul Sharma")

        # ── Row 2: Class | Section ───────────────────────────────────
        self._make_label(inner, "Class *",   4, 0)
        self._make_label(inner, "Section *", 4, 2)

        v_cls = tk.StringVar(); self.inputs["class"]   = v_cls
        v_sec = tk.StringVar(); self.inputs["section"] = v_sec
        self._make_combo(inner, v_cls, ["1","2","3","4","5","6","7","8","9","10","11","12"], 5, 0, "1")
        self._make_combo(inner, v_sec, ["A","B","C"],    5, 2, "A")

        # ── Row 3: Date of Birth | Gender ────────────────────────────
        self._make_label(inner, "Date of Birth", 6, 0)
        self._make_label(inner, "Gender *",      6, 2)

        v_dob    = tk.StringVar(); self.inputs["dob"]    = v_dob
        v_gender = tk.StringVar(); self.inputs["gender"] = v_gender
        self._make_entry(inner, v_dob, 7, 0, "YYYY-MM-DD")
        self._make_combo(inner, v_gender,
                         ["Male","Female","Other"], 7, 2, "Male")

        # ── Row 4: Phone | Email ─────────────────────────────────────
        self._make_label(inner, "Phone Number",  8, 0)
        self._make_label(inner, "Email Address", 8, 2)

        v_phone = tk.StringVar(); self.inputs["phone"] = v_phone
        v_email = tk.StringVar(); self.inputs["email"] = v_email
        self._make_entry(inner, v_phone, 9, 0, "10-digit number")
        self._make_entry(inner, v_email, 9, 2, "student@example.com")

        # ── Divider ──────────────────────────────────────────────────
        ttk.Separator(inner, orient="horizontal").grid(
            row=10, column=0, columnspan=4,
            sticky="ew", pady=(10, 20))

        # ── Buttons ──────────────────────────────────────────────────
        btn_frame = ttk.Frame(inner, style="Card.TFrame")
        btn_frame.grid(row=11, column=0, columnspan=4, sticky="w")

        ttk.Button(btn_frame, text="💾  Save Student Record",
                   style="Success.TButton",
                   command=self._save_student).pack(side="left", padx=(0, 12))

        ttk.Button(btn_frame, text="🔄  Clear Form",
                   style="Secondary.TButton",
                   command=self._clear_form).pack(side="left")

        self.msg_lbl = ttk.Label(btn_frame, text="",
                                 font=ui_styles.FONT_SMALL,
                                 style="Card.TLabel")
        self.msg_lbl.pack(side="left", padx=15)

    # ── Actions ──────────────────────────────────────────────────────
    def _clear_form(self):
        defaults = {"class": "12", "section": "A", "gender": "Male"}
        placeholders = {
            "roll_no": "e.g. 101",
            "name":    "e.g. Rahul Sharma",
            "dob":     "YYYY-MM-DD",
            "phone":   "10-digit number",
            "email":   "student@example.com",
        }
        for key, var in self.inputs.items():
            if key in defaults:
                var.set(defaults[key])
            else:
                var.set("")
        self.msg_lbl.configure(text="", foreground=ui_styles.COLOR_TEXT_MUTED)

    def _get_val(self, key):
        """Return clean value, ignore placeholder text."""
        placeholders = {
            "roll_no": "e.g. 101",
            "name":    "e.g. Rahul Sharma",
            "dob":     "YYYY-MM-DD",
            "phone":   "10-digit number",
            "email":   "student@example.com",
        }
        val = self.inputs[key].get().strip()
        return "" if val == placeholders.get(key, "") else val

    def _save_student(self):
        roll_no = self._get_val("roll_no")
        name    = self._get_val("name")
        cls     = self.inputs["class"].get().strip()
        sec     = self.inputs["section"].get().strip()
        dob     = self._get_val("dob")
        gender  = self.inputs["gender"].get().strip()
        phone   = self._get_val("phone")
        email   = self._get_val("email")

        if not roll_no or not name or not cls or not sec or not gender:
            messagebox.showwarning(
                "Validation Error",
                "Please fill in all mandatory fields (Roll No, Name, Class, Section, Gender).")
            return

        if not roll_no.isalnum():
            messagebox.showwarning(
                "Validation Error",
                "Roll Number should be alphanumeric (e.g. 101 or S101).")
            return

        if phone and (not phone.isdigit() or len(phone) < 7):
            messagebox.showwarning(
                "Validation Error",
                "Please enter a valid phone number (digits only, min 7).")
            return

        student_data = {
            "roll_no": roll_no, "name": name,
            "class": cls,       "section": sec,
            "dob": dob,         "gender": gender,
            "phone": phone,     "email": email,
        }

        success, msg = database.add_student(student_data)
        if success:
            self.msg_lbl.configure(text="✅ " + msg,
                                   foreground=ui_styles.COLOR_SUCCESS)
            self._clear_form()
        else:
            messagebox.showerror("Error", msg)
