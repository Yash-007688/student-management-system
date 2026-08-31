"""
screens/login.py
----------------
Login screen with role selection (Admin / Teacher / Student).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles

# Demo credentials hint per role
_HINTS = {
    "Admin":   "admin / admin123",
    "Teacher": "teacher1 / teach123  |  teacher2 / teach456",
    "Student": "aarav / student101  |  diya / student102  |  rohan / student103",
}


class LoginScreen(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self):
        center = ttk.Frame(self)
        center.grid(row=0, column=0)

        card = ttk.Frame(center, style="Card.TFrame", padding=40)
        card.pack()

        # Icon + title
        ttk.Label(card, text="🎓", font=("Segoe UI", 40),
                  style="Card.TLabel").pack(pady=(0, 6))

        ttk.Label(card, text="Student Management System",
                  font=ui_styles.FONT_TITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").pack(pady=(0, 4))

        ttk.Label(card,
                  text="Sign in to access the system",
                  style="CardMuted.TLabel").pack(pady=(0, 28))

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x", ipadx=10)

        # Role selector
        ttk.Label(form, text="Login As",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").pack(anchor="w", pady=(0, 4))

        self.role_var = tk.StringVar(value="Admin")
        role_cb = ttk.Combobox(form, textvariable=self.role_var,
                               values=["Admin", "Teacher", "Student"],
                               state="readonly", width=32)
        role_cb.pack(fill="x", pady=(0, 16))
        role_cb.bind("<<ComboboxSelected>>", self._on_role_change)

        # Username
        ttk.Label(form, text="Username",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").pack(anchor="w", pady=(0, 4))

        self.username_var = tk.StringVar(value="admin")
        self.username_entry = ttk.Entry(form, textvariable=self.username_var,
                                        width=34)
        self.username_entry.pack(fill="x", pady=(0, 14))

        # Password
        ttk.Label(form, text="Password",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").pack(anchor="w", pady=(0, 4))

        self.password_var = tk.StringVar(value="admin123")
        self.password_entry = ttk.Entry(form, textvariable=self.password_var,
                                        show="•", width=34)
        self.password_entry.pack(fill="x", pady=(0, 6))

        # Show password
        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text="Show Password",
                        variable=self.show_var,
                        command=self._toggle_pw).pack(anchor="w", pady=(0, 22))

        # Buttons
        btn_row = ttk.Frame(form, style="Card.TFrame")
        btn_row.pack(fill="x")

        ttk.Button(btn_row, text="Login",
                   style="Primary.TButton",
                   command=self._handle_login).pack(
            side="left", fill="x", expand=True, padx=(0, 6))

        ttk.Button(btn_row, text="Exit",
                   style="Secondary.TButton",
                   command=self.winfo_toplevel().destroy).pack(side="right")

        # Hint label
        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=(22, 12))

        self.hint_lbl = ttk.Label(card,
                                  text=f"Demo: {_HINTS['Admin']}",
                                  style="CardMuted.TLabel",
                                  font=ui_styles.FONT_SMALL,
                                  wraplength=340,
                                  justify="center")
        self.hint_lbl.pack()

        # Key bindings
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        self.username_entry.bind("<Return>",
                                 lambda e: self.password_entry.focus())

    def _on_role_change(self, event=None):
        role = self.role_var.get()
        self.username_var.set("")
        self.password_var.set("")
        self.hint_lbl.configure(text=f"Demo: {_HINTS[role]}")

    def _toggle_pw(self):
        self.password_entry.configure(
            show="" if self.show_var.get() else "•")

    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        role_selected = self.role_var.get().lower()   # admin/teacher/student

        if not username or not password:
            messagebox.showwarning("Missing Fields",
                                   "Please enter username and password.")
            return

        user = database.verify_login(username, password)
        if not user:
            messagebox.showerror("Login Failed",
                                 "Invalid username or password.")
            return

        # Verify role matches
        if user["role"] != role_selected:
            messagebox.showerror(
                "Wrong Role",
                f"This account is registered as '{user['role'].capitalize()}'.\n"
                f"Please select the correct role.")
            return

        self.on_login_success(user)
