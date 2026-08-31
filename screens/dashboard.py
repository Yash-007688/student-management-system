"""
screens/dashboard.py
--------------------
Main Dashboard hub for the Student Management System.
Features system stats and quick navigation cards to all functions.
"""

import tkinter as tk
from tkinter import ttk
import database
import ui_styles


class DashboardScreen(ttk.Frame):
    def __init__(self, parent, navigate_callback, logout_callback, user_name="Admin"):
        super().__init__(parent)
        self.navigate_callback = navigate_callback
        self.logout_callback = logout_callback
        self.user_name = user_name

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        # 1. Top Welcome Bar
        top_bar = ttk.Frame(self, style="Card.TFrame", padding=(25, 15))
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        welcome_frame = ttk.Frame(top_bar, style="Card.TFrame")
        welcome_frame.pack(side="left")

        ttk.Label(
            welcome_frame,
            text=f"Welcome back, {self.user_name} 👋",
            font=ui_styles.FONT_TITLE,
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            welcome_frame,
            text="Student Management & Academic Record System",
            style="CardMuted.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        # Logout Button
        logout_btn = ttk.Button(
            top_bar,
            text="🚪 Logout",
            style="Danger.TButton",
            command=self.logout_callback
        )
        logout_btn.pack(side="right")

        # 2. Main Scrollable or Centered Dashboard Body
        content_frame = ttk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_frame.columnconfigure(0, weight=1)

        # Quick Stats Banner
        self._build_stats_section(content_frame)

        # Action Cards Grid
        self._build_navigation_grid(content_frame)

    def _build_stats_section(self, parent):
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill="x", pady=(0, 15))

        total_students = len(database.get_all_students())

        # Simple Stat Card
        stat_card = ttk.Frame(stats_frame, style="Card.TFrame", padding=(20, 15))
        stat_card.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Label(stat_card, text="Total Enrolled Students", style="CardMuted.TLabel").pack(anchor="w")
        self.lbl_total_students = ttk.Label(
            stat_card,
            text=str(total_students),
            font=("Segoe UI", 20, "bold"),
            foreground=ui_styles.COLOR_PRIMARY,
            style="Card.TLabel"
        )
        self.lbl_total_students.pack(anchor="w", pady=(4, 0))

        # System Status Card
        status_card = ttk.Frame(stats_frame, style="Card.TFrame", padding=(20, 15))
        status_card.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ttk.Label(status_card, text="System Status", style="CardMuted.TLabel").pack(anchor="w")
        ttk.Label(
            status_card,
            text="🟢 Active (Class 12 Session)",
            font=ui_styles.FONT_HEADING,
            foreground=ui_styles.COLOR_SUCCESS,
            style="Card.TLabel"
        ).pack(anchor="w", pady=(6, 0))

    def _build_navigation_grid(self, parent):
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill="both", expand=True)

        for col in range(3):
            grid_frame.columnconfigure(col, weight=1)

        nav_items = [
            ("👨‍🎓 View All Students", "Browse, view and filter all student records", "view_students", ui_styles.COLOR_PRIMARY),
            ("➕ Add New Student", "Register a new student into the system", "add_student", ui_styles.COLOR_SUCCESS),
            ("🔍 Search Student", "Search records by Roll Number or Name", "search_student", ui_styles.COLOR_SECONDARY),
            ("✏️ Update Student", "Edit and update existing student details", "update_student", ui_styles.COLOR_WARNING),
            ("🗑️ Delete Student", "Remove student records with verification", "delete_student", ui_styles.COLOR_DANGER),
            ("📊 Marks Entry", "Enter and update subject-wise student marks", "marks_entry", ui_styles.COLOR_PRIMARY),
            ("📋 Results & Reports", "Generate student scorecard, percentage & grades", "result_view", ui_styles.COLOR_SUCCESS),
        ]

        row = 0
        col = 0
        for title, desc, screen_key, accent_color in nav_items:
            card = ttk.Frame(grid_frame, style="Card.TFrame", padding=16)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

            ttk.Label(
                card,
                text=title,
                font=ui_styles.FONT_SUBTITLE,
                foreground=accent_color,
                style="Card.TLabel"
            ).pack(anchor="w", pady=(0, 4))

            ttk.Label(
                card,
                text=desc,
                style="CardMuted.TLabel",
                wraplength=200
            ).pack(anchor="w", pady=(0, 12))

            action_btn = ttk.Button(
                card,
                text="Open →",
                style="Secondary.TButton",
                command=lambda k=screen_key: self.navigate_callback(k)
            )
            action_btn.pack(anchor="e")

            col += 1
            if col >= 3:
                col = 0
                row += 1

    def refresh_data(self):
        """Refreshes counters when returning to dashboard."""
        total = len(database.get_all_students())
        self.lbl_total_students.configure(text=str(total))
