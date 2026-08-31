"""
screens/login.py
----------------
Login screen for the Student Management System.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class LoginScreen(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self):
        # Outer center container
        center_box = ttk.Frame(self)
        center_box.grid(row=0, column=0, padx=20, pady=20)

        # Card Frame
        card = ttk.Frame(center_box, style="Card.TFrame", padding=35)
        card.pack(fill="both", expand=True)

        # System Icon / Title
        title_icon = ttk.Label(
            card,
            text="🎓",
            font=("Segoe UI", 36),
            style="Card.TLabel"
        )
        title_icon.pack(pady=(0, 5))

        title_lbl = ttk.Label(
            card,
            text="Student Management System",
            font=ui_styles.FONT_TITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        )
        title_lbl.pack(pady=(0, 4))

        subtitle_lbl = ttk.Label(
            card,
            text="Sign in to access student records and results",
            style="CardMuted.TLabel"
        )
        subtitle_lbl.pack(pady=(0, 25))

        # Form fields container
        form_frame = ttk.Frame(card, style="Card.TFrame")
        form_frame.pack(fill="x")

        # Username
        ttk.Label(form_frame, text="Username", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(anchor="w", pady=(0, 4))
        self.username_var = tk.StringVar(value="admin")
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=32)
        self.username_entry.pack(fill="x", pady=(0, 15))

        # Password
        ttk.Label(form_frame, text="Password", font=ui_styles.FONT_BODY_BOLD, style="Card.TLabel").pack(anchor="w", pady=(0, 4))
        self.password_var = tk.StringVar(value="admin123")
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="•", width=32)
        self.password_entry.pack(fill="x", pady=(0, 5))

        # Show password toggle
        self.show_pass_var = tk.BooleanVar(value=False)
        show_pass_cb = ttk.Checkbutton(
            form_frame,
            text="Show Password",
            variable=self.show_pass_var,
            command=self._toggle_password
        )
        show_pass_cb.pack(anchor="w", pady=(0, 20))

        # Buttons Container
        btn_frame = ttk.Frame(form_frame, style="Card.TFrame")
        btn_frame.pack(fill="x")

        login_btn = ttk.Button(
            btn_frame,
            text="Login",
            style="Primary.TButton",
            command=self._handle_login
        )
        login_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        exit_btn = ttk.Button(
            btn_frame,
            text="Exit",
            style="Secondary.TButton",
            command=self.winfo_toplevel().destroy
        )
        exit_btn.pack(side="right", padx=(5, 0))

        # Demo Credentials hint
        hint_frame = ttk.Frame(card, style="Card.TFrame")
        hint_frame.pack(fill="x", pady=(20, 0))
        hint_lbl = ttk.Label(
            hint_frame,
            text="Default demo login: admin / admin123",
            style="CardMuted.TLabel",
            font=ui_styles.FONT_SMALL
        )
        hint_lbl.pack()

        # Enter key triggers login
        self.password_entry.bind("<Return>", lambda event: self._handle_login())
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())

    def _toggle_password(self):
        if self.show_pass_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")

    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Fields", "Please enter both username and password.")
            return

        if database.verify_login(username, password):
            self.on_login_success(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")
