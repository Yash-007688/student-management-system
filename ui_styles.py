"""
ui_styles.py
------------
Defines color palette, fonts, and ttk styling for the Student Management System.
Keeps UI styling centralized and consistent across all screens.
"""

import tkinter as tk
from tkinter import ttk

# --- Color Palette ---
COLOR_PRIMARY = "#1E3A8A"       # Deep Navy Blue
COLOR_PRIMARY_HOVER = "#1E40AF" # Blue Hover
COLOR_SECONDARY = "#3B82F6"     # Accent Blue
COLOR_SUCCESS = "#10B981"       # Emerald Green
COLOR_DANGER = "#EF4444"        # Crimson Red
COLOR_WARNING = "#F59E0B"       # Amber
COLOR_BG = "#F8FAFC"            # Slate light background
COLOR_CARD_BG = "#FFFFFF"       # White for panels and cards
COLOR_TEXT_MAIN = "#0F172A"     # Dark Slate for primary text
COLOR_TEXT_MUTED = "#64748B"    # Slate grey for subtitles/placeholders
COLOR_BORDER = "#CBD5E1"        # Light Grey for borders

# --- Font Configurations ---
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 13, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_BADGE = ("Segoe UI", 9, "bold")


def apply_theme(root):
    """
    Applies custom styling to standard ttk widgets.
    """
    style = ttk.Style(root)
    
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=COLOR_BG)

    # Frame styles
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_CARD_BG)
    style.configure("Nav.TFrame", background=COLOR_PRIMARY)

    # Label styles
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT_MAIN, font=FONT_BODY)
    style.configure("Card.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_MAIN, font=FONT_BODY)
    style.configure("CardMuted.TLabel", background=COLOR_CARD_BG, foreground=COLOR_TEXT_MUTED, font=FONT_SMALL)
    style.configure("Header.TLabel", background=COLOR_BG, foreground=COLOR_PRIMARY, font=FONT_TITLE)
    style.configure("CardHeader.TLabel", background=COLOR_CARD_BG, foreground=COLOR_PRIMARY, font=FONT_SUBTITLE)
    style.configure("NavHeader.TLabel", background=COLOR_PRIMARY, foreground="#FFFFFF", font=FONT_SUBTITLE)

    # Entry styles
    style.configure(
        "TEntry",
        padding=6,
        fieldbackground="#FFFFFF",
        foreground=COLOR_TEXT_MAIN,
        bordercolor=COLOR_BORDER,
        font=FONT_BODY
    )

    # Combobox styles
    style.configure(
        "TCombobox",
        padding=5,
        fieldbackground="#FFFFFF",
        foreground=COLOR_TEXT_MAIN,
        font=FONT_BODY
    )

    # Buttons
    style.configure(
        "Primary.TButton",
        background=COLOR_PRIMARY,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        padding=(14, 8),
        borderwidth=0
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLOR_PRIMARY_HOVER), ("pressed", COLOR_PRIMARY_HOVER)]
    )

    style.configure(
        "Success.TButton",
        background=COLOR_SUCCESS,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        padding=(14, 8),
        borderwidth=0
    )
    style.map(
        "Success.TButton",
        background=[("active", "#059669"), ("pressed", "#059669")]
    )

    style.configure(
        "Danger.TButton",
        background=COLOR_DANGER,
        foreground="#FFFFFF",
        font=FONT_BODY_BOLD,
        padding=(14, 8),
        borderwidth=0
    )
    style.map(
        "Danger.TButton",
        background=[("active", "#DC2626"), ("pressed", "#DC2626")]
    )

    style.configure(
        "Secondary.TButton",
        background="#E2E8F0",
        foreground=COLOR_TEXT_MAIN,
        font=FONT_BODY_BOLD,
        padding=(12, 7),
        borderwidth=0
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#CBD5E1"), ("pressed", "#CBD5E1")]
    )

    # Treeview
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground=COLOR_TEXT_MAIN,
        rowheight=28,
        fieldbackground="#FFFFFF",
        font=FONT_BODY,
        bordercolor=COLOR_BORDER,
        borderwidth=1
    )
    style.configure(
        "Treeview.Heading",
        background="#E2E8F0",
        foreground=COLOR_PRIMARY,
        font=FONT_BODY_BOLD,
        padding=(8, 6),
        relief="flat"
    )
    style.map(
        "Treeview",
        background=[("selected", COLOR_SECONDARY)],
        foreground=[("selected", "#FFFFFF")]
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#CBD5E1")]
    )

    # Scrollbars
    style.configure(
        "Vertical.TScrollbar",
        background="#E2E8F0",
        troughcolor=COLOR_BG,
        borderwidth=0,
        arrowsize=14
    )
    style.configure(
        "Horizontal.TScrollbar",
        background="#E2E8F0",
        troughcolor=COLOR_BG,
        borderwidth=0,
        arrowsize=14
    )

    # LabelFrames
    style.configure(
        "TLabelframe",
        background=COLOR_CARD_BG,
        foreground=COLOR_PRIMARY,
        bordercolor=COLOR_BORDER,
        borderwidth=1,
        padding=10
    )
    style.configure(
        "TLabelframe.Label",
        background=COLOR_CARD_BG,
        foreground=COLOR_PRIMARY,
        font=FONT_HEADING
    )
