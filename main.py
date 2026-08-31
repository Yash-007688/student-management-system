"""
main.py
-------
Entry point for the Student Management System application.
"""

import tkinter as tk
from tkinter import ttk
import ui_styles
from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.student_add import AddStudentScreen
from screens.student_search import SearchStudentScreen
from screens.student_update import UpdateStudentScreen
from screens.student_view import ViewStudentsScreen
from screens.marks_entry import MarksEntryScreen
from screens.result_view import ResultViewScreen


class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Apply theme
        ui_styles.apply_theme(self)

        # Container that fills the whole window
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.screens = {}
        self.current_screen = None
        self.username_on_login = "Admin"

        self._init_screens()
        self.show_screen("login")

    def _init_screens(self):
        """Build all screens and place them on the same grid cell so they stack."""

        # Login screen — needs its own on_login_success callback
        login = LoginScreen(self.container, self._on_login_success)
        login.grid(row=0, column=0, sticky="nsew")
        self.screens["login"] = login

        # Dashboard — needs navigate + logout + username
        dashboard = DashboardScreen(
            self.container,
            self._navigate,
            self._on_logout,
            self.username_on_login
        )
        dashboard.grid(row=0, column=0, sticky="nsew")
        self.screens["dashboard"] = dashboard

        # All other screens — only need navigate/back callback
        simple_screens = {
            "add_student":    AddStudentScreen,
            "search_student": SearchStudentScreen,
            "update_student": UpdateStudentScreen,
            "view_students":  ViewStudentsScreen,
            "marks_entry":    MarksEntryScreen,
            "result_view":    ResultViewScreen,
        }

        for name, cls in simple_screens.items():
            frame = cls(self.container, lambda: self._navigate("dashboard"))
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = frame

    # ------------------------------------------------------------------
    def _navigate(self, screen_key):
        self.show_screen(screen_key)

    def _on_login_success(self, username):
        self.username_on_login = username
        # Update the welcome label on dashboard with actual username
        dash = self.screens.get("dashboard")
        if dash:
            dash.user_name = username
            # Rebuild the welcome text
            try:
                for widget in dash.winfo_children():
                    widget.destroy()
                dash._build_ui()
            except Exception:
                pass
        self.show_screen("dashboard")

    def _on_logout(self):
        self.username_on_login = None
        self.show_screen("login")

    # ------------------------------------------------------------------
    def show_screen(self, screen_key):
        screen = self.screens.get(screen_key)
        if not screen:
            print(f"[WARN] Screen '{screen_key}' not found!")
            return

        screen.tkraise()

        if screen_key == "dashboard":
            if hasattr(screen, "refresh_data"):
                screen.refresh_data()

        self.current_screen = screen_key


if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()
