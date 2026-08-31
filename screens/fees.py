"""
screens/fees.py
---------------
Fees Management screen — Admin only.
View all fees, add payment for a student.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import ui_styles


class FeesScreen(ttk.Frame):
    def __init__(self, parent, on_back_callback):
        super().__init__(parent)
        self.on_back_callback = on_back_callback

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        # Top bar
        top_bar = ttk.Frame(self, style="Card.TFrame", padding=(20, 12))
        top_bar.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        ttk.Button(top_bar, text="← Back to Dashboard",
                   style="Secondary.TButton",
                   command=self.on_back_callback).pack(side="left")

        ttk.Label(top_bar, text="Fees Management",
                  font=ui_styles.FONT_TITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").pack(side="left", padx=20)

        ttk.Button(top_bar, text="🔄 Refresh",
                   style="Secondary.TButton",
                   command=self.refresh_table).pack(side="right")

        # Main content
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        # ── Add Payment card ─────────────────────────────────────────
        pay_card = ttk.Frame(content, style="Card.TFrame", padding=20)
        pay_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(pay_card, text="Add Payment",
                  font=ui_styles.FONT_SUBTITLE,
                  foreground=ui_styles.COLOR_PRIMARY,
                  style="Card.TLabel").grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 12))

        ttk.Label(pay_card, text="Roll Number:",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8))

        self.pay_roll_var = tk.StringVar()
        ttk.Entry(pay_card, textvariable=self.pay_roll_var,
                  width=14).grid(row=1, column=1, padx=(0, 20))

        ttk.Label(pay_card, text="Amount (₹):",
                  font=ui_styles.FONT_BODY_BOLD,
                  style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=(0, 8))

        self.pay_amt_var = tk.StringVar()
        ttk.Entry(pay_card, textvariable=self.pay_amt_var,
                  width=14).grid(row=1, column=3, padx=(0, 20))

        ttk.Button(pay_card, text="💰 Add Payment",
                   style="Success.TButton",
                   command=self._add_payment).grid(row=1, column=4)

        # ── Fees Table ───────────────────────────────────────────────
        table_card = ttk.Frame(content, style="Card.TFrame", padding=20)
        table_card.grid(row=1, column=0, sticky="nsew")
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        ttk.Label(table_card, text="All Student Fees Records",
                  font=ui_styles.FONT_SUBTITLE,
                  style="Card.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))

        tree_frame = ttk.Frame(table_card)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        cols = ("roll_no", "name", "class", "section",
                "total_fees", "paid", "pending", "status", "last_payment")
        self.tree = ttk.Treeview(tree_frame, columns=cols,
                                 show="headings", selectmode="browse")

        headings = [
            ("roll_no",      "Roll No",      80),
            ("name",         "Name",        160),
            ("class",        "Class",        60),
            ("section",      "Sec",          50),
            ("total_fees",   "Total (₹)",    90),
            ("paid",         "Paid (₹)",     90),
            ("pending",      "Pending (₹)", 100),
            ("status",       "Status",       90),
            ("last_payment", "Last Payment", 110),
        ]
        for cid, cname, cw in headings:
            self.tree.heading(cid, text=cname, anchor="w")
            self.tree.column(cid, width=cw, anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Tag colors for status
        self.tree.tag_configure("Paid",    foreground=ui_styles.COLOR_SUCCESS)
        self.tree.tag_configure("Pending", foreground=ui_styles.COLOR_DANGER)
        self.tree.tag_configure("Partial", foreground=ui_styles.COLOR_WARNING)

        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for f in database.get_all_fees():
            tag = f.get("status", "Pending")
            self.tree.insert("", "end", tags=(tag,), values=(
                f["roll_no"], f["name"], f["class"], f["section"],
                f"₹{f['total_fees']}", f"₹{f['paid']}",
                f"₹{f['pending']}", f["status"], f["last_payment"]
            ))

    def _add_payment(self):
        roll = self.pay_roll_var.get().strip()
        amt_str = self.pay_amt_var.get().strip()

        if not roll or not amt_str:
            messagebox.showwarning("Input Needed",
                                   "Please enter Roll Number and Amount.")
            return
        try:
            amount = float(amt_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Amount",
                                   "Please enter a valid positive amount.")
            return

        success, msg = database.update_fees(roll, amount)
        if success:
            messagebox.showinfo("Success", msg)
            self.pay_roll_var.set("")
            self.pay_amt_var.set("")
            self.refresh_table()
        else:
            messagebox.showerror("Error", msg)
