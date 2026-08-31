"""
main.py
-------
Entry point — role-based navigation (admin / teacher / student).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ui_styles

from screens.login           import LoginScreen
from screens.dashboard       import DashboardScreen
from screens.student_add     import AddStudentScreen
from screens.student_search  import SearchStudentScreen
from screens.student_update  import UpdateStudentScreen
from screens.student_view    import ViewStudentsScreen
from screens.marks_entry     import MarksEntryScreen
from screens.result_view     import ResultViewScreen
from screens.fees            import FeesScreen
from screens.student_dashboard  import StudentDashboard
from screens.teacher_dashboard  import TeacherDashboard


class StudentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1200x720")
        self.minsize(1000, 620)

        ui_styles.apply_theme(self)

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.current_user = None   # full user dict after login
        self.screens = {}

        self._init_screens()
        self.show_screen("login")

    # ── Screen Initialization ─────────────────────────────────────────
    def _init_screens(self):
        # Login
        s = LoginScreen(self.container, self._on_login_success)
        s.grid(row=0, column=0, sticky="nsew")
        self.screens["login"] = s

        # Admin screens
        s = DashboardScreen(self.container, self._navigate,
                            self._on_logout, "Admin")
        s.grid(row=0, column=0, sticky="nsew")
        self.screens["dashboard"] = s

        for name, cls in {
            "add_student":    AddStudentScreen,
            "search_student": SearchStudentScreen,
            "update_student": UpdateStudentScreen,
            "view_students":  ViewStudentsScreen,
            "marks_entry":    MarksEntryScreen,
            "result_view":    ResultViewScreen,
            "fees":           FeesScreen,
        }.items():
            s = cls(self.container, lambda: self._navigate("dashboard"))
            s.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = s

        # Teacher / Student dashboards are created on login (dynamic)
        # Placeholders so show_screen won't crash before login
        self.screens["teacher_dashboard"] = None
        self.screens["student_dashboard"] = None

    # ── Login / Logout ────────────────────────────────────────────────
    def _on_login_success(self, user):
        """user = dict from database.verify_login"""
        self.current_user = user
        role = user["role"]

        if role == "admin":
            dash = self.screens["dashboard"]
            dash.user_name = user["display_name"]
            # Rebuild dashboard welcome text
            try:
                for w in dash.winfo_children():
                    w.destroy()
                dash._build_ui()
            except Exception:
                pass
            self.show_screen("dashboard")

        elif role == "teacher":
            # Rebuild teacher dashboard with current user info
            old = self.screens.get("teacher_dashboard")
            if old:
                old.destroy()
            td = TeacherDashboard(self.container, self._on_logout, user)
            td.grid(row=0, column=0, sticky="nsew")
            self.screens["teacher_dashboard"] = td
            self.show_screen("teacher_dashboard")

        elif role == "student":
            old = self.screens.get("student_dashboard")
            if old:
                old.destroy()
            sd = StudentDashboard(self.container, self._on_logout, user)
            sd.grid(row=0, column=0, sticky="nsew")
            self.screens["student_dashboard"] = sd
            self.show_screen("student_dashboard")

    def _on_logout(self):
        self.current_user = None
        self.show_screen("login")

    # ── Navigation ────────────────────────────────────────────────────
    def _navigate(self, screen_key):
        # Guard: only admin can access admin screens
        if self.current_user and self.current_user["role"] != "admin":
            messagebox.showwarning("Access Denied",
                                   "You don't have permission for this page.")
            return
        self.show_screen(screen_key)

    def show_screen(self, screen_key):
        screen = self.screens.get(screen_key)
        if not screen:
            return
        screen.tkraise()
        if screen_key == "dashboard" and hasattr(screen, "refresh_data"):
            screen.refresh_data()


if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()
