"""
Main application window for PhishGuard.

Defines the `App` class (the root CustomTkinter window with a sidebar +
tabbed content area) and the Dashboard view itself. Other tabs
(analyzer_tab, education_tab, etc.) are added here incrementally in later
steps and simply need to be instantiated inside `App._build_tabs`.
"""
from __future__ import annotations

import tkinter as tk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analyzer.content_analyzer import analyze_content, total_content_score
from database.database import Database
from gui.hackerzone_tab import HackerZoneFrame
from utils.logger import get_logger
from utils.validators import clamp_text

logger = get_logger(__name__)

SIDEBAR_WIDTH = 200


class App(ctk.CTk):
    """Root application window: sidebar navigation + swappable content frame."""

    def __init__(self, db: Database) -> None:
        super().__init__()
        self.db = db

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        self._current_frame_name: str | None = None

        # Show the dashboard by default on launch.
        self.show_frame("Dashboard")

    # ------------------------------------------------------------------ #
    # Layout construction
    # ------------------------------------------------------------------ #
    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        title = ctk.CTkLabel(
            self.sidebar,
            text="🛡  PhishGuard",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(24, 4), sticky="w")

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Awareness & Analysis Toolkit",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 24), sticky="w")

        # Nav buttons. Tabs marked "coming soon" get a lightweight
        # placeholder frame until their own build step; Dashboard and
        # Hacker Zone are fully built.
        nav_items = [
            "Dashboard",
            "Email Analyzer",
            "Link Analysis",
            "Education Center",
            "History",
            "Reports",
            "Settings",
            "Hacker Zone 🕶️",
        ]

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for i, label in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color="gray25",
                command=lambda name=label: self.show_frame(name),
            )
            btn.grid(row=i, column=0, padx=12, pady=4, sticky="ew")
            self._nav_buttons[label] = btn

        mode_label = ctk.CTkLabel(self.sidebar, text="Appearance", font=ctk.CTkFont(size=11))
        mode_label.grid(row=13, column=0, padx=20, pady=(16, 4), sticky="w")

        self.appearance_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=self._on_appearance_change,
        )
        self.appearance_menu.grid(row=14, column=0, padx=12, pady=(0, 16), sticky="ew")
        self.appearance_menu.set("Dark")

    def _build_content_area(self) -> None:
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._frames: dict[str, ctk.CTkFrame] = {}
        self._frames["Dashboard"] = DashboardFrame(self.content, db=self.db)
        self._frames["Hacker Zone 🕶️"] = HackerZoneFrame(self.content)

        coming_soon = {
            "Email Analyzer": "Paste or upload an .eml file for full header, link, and content analysis.",
            "Link Analysis": "Deep-dive URL structure checks: IP-literal links, suspicious TLDs, HTTPS usage.",
            "Education Center": "Full phishing-type reference material and the Spot the Phish quiz in one place.",
            "History": "Searchable, filterable log of every analysis you've run, backed by SQLite.",
            "Reports": "Export a PDF/CSV summary of any past analysis.",
            "Settings": "Toggle optional features (e.g. domain-age lookups) and manage local data.",
        }
        for name, description in coming_soon.items():
            self._frames[name] = ComingSoonFrame(self.content, title=name, description=description)

        for frame in self._frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def show_frame(self, name: str) -> None:
        """Raise the named frame to the top of the content area."""
        frame = self._frames.get(name)
        if frame is None:
            logger.warning("Requested unknown frame: %s", name)
            return

        previous = self._frames.get(self._current_frame_name) if self._current_frame_name else None
        if previous is not None and previous is not frame and hasattr(previous, "on_hide"):
            previous.on_hide()

        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()
        self._current_frame_name = name

    def _on_appearance_change(self, mode: str) -> None:
        ctk.set_appearance_mode(mode.lower())
        logger.debug("Appearance mode changed to %s", mode)


class ComingSoonFrame(ctk.CTkFrame):
    """Lightweight placeholder for tabs not yet built in this step."""

    def __init__(self, master, title: str, description: str) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=26, weight="bold"))
        header.grid(row=0, column=0, sticky="w", pady=(0, 12))

        badge = ctk.CTkLabel(
            self, text="COMING IN A NEXT BUILD STEP",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray50",
        )
        badge.grid(row=1, column=0, sticky="w", pady=(0, 8))

        desc = ctk.CTkLabel(
            self, text=description, font=ctk.CTkFont(size=13),
            text_color="gray70", wraplength=600, justify="left",
        )
        desc.grid(row=2, column=0, sticky="w")


class DashboardFrame(ctk.CTkFrame):
    """The at-a-glance overview: totals, risk breakdown, awareness score."""

    def __init__(self, master: ctk.CTkFrame, db: Database) -> None:
        super().__init__(master, fg_color="transparent")
        self.db = db

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        header = ctk.CTkLabel(
            self, text="Dashboard", font=ctk.CTkFont(size=26, weight="bold")
        )
        header.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 16))

        self._stat_cards: dict[str, ctk.CTkLabel] = {}
        self._build_stat_cards()

        self._build_chart_and_quickscan()

        info = ctk.CTkLabel(
            self,
            text=(
                "This dashboard summarizes emails you have analyzed locally. "
                "No data leaves this application."
            ),
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            justify="left",
        )
        info.grid(row=3, column=0, columnspan=4, sticky="w", pady=(16, 0))

        self.on_show()

    def _build_chart_and_quickscan(self) -> None:
        self.grid_rowconfigure(2, weight=1)

        # --- Risk distribution chart (left) ---
        chart_card = ctk.CTkFrame(self, corner_radius=12)
        chart_card.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(0, 10), pady=(16, 0))
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(1, weight=1)

        chart_title = ctk.CTkLabel(
            chart_card, text="Risk Distribution", font=ctk.CTkFont(size=15, weight="bold")
        )
        chart_title.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        self._figure = Figure(figsize=(4, 3), dpi=100)
        self._figure.patch.set_alpha(0)
        self._axis = self._figure.add_subplot(111)
        self._chart_canvas = FigureCanvasTkAgg(self._figure, master=chart_card)
        self._chart_canvas.get_tk_widget().grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        # --- Quick Scan (right): paste text, get instant content-pattern findings ---
        scan_card = ctk.CTkFrame(self, corner_radius=12)
        scan_card.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=(10, 0), pady=(16, 0))
        scan_card.grid_columnconfigure(0, weight=1)
        scan_card.grid_rowconfigure(2, weight=1)

        scan_title = ctk.CTkLabel(
            scan_card, text="Quick Scan", font=ctk.CTkFont(size=15, weight="bold")
        )
        scan_title.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        scan_sub = ctk.CTkLabel(
            scan_card,
            text="Paste suspicious email text for an instant social-engineering pattern check.",
            font=ctk.CTkFont(size=11), text_color="gray60", wraplength=380, justify="left",
        )
        scan_sub.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        self._scan_input = ctk.CTkTextbox(scan_card, height=90)
        self._scan_input.grid(row=2, column=0, padx=16, pady=(0, 8), sticky="nsew")

        scan_btn = ctk.CTkButton(scan_card, text="Scan Text", command=self._run_quick_scan)
        scan_btn.grid(row=3, column=0, padx=16, pady=(0, 8), sticky="w")

        self._scan_results = ctk.CTkScrollableFrame(scan_card, height=110)
        self._scan_results.grid(row=4, column=0, padx=16, pady=(0, 14), sticky="nsew")
        self._scan_results.grid_columnconfigure(0, weight=1)

    def _run_quick_scan(self) -> None:
        raw_text = clamp_text(self._scan_input.get("1.0", "end"))

        for widget in self._scan_results.winfo_children():
            widget.destroy()

        if not raw_text.strip():
            ctk.CTkLabel(
                self._scan_results, text="Paste some text above first.",
                text_color="gray60", font=ctk.CTkFont(size=12),
            ).grid(row=0, column=0, sticky="w")
            return

        findings = analyze_content(raw_text)
        score = total_content_score(findings)

        if not findings:
            ctk.CTkLabel(
                self._scan_results,
                text=f"No obvious social-engineering patterns detected (score {score}/100).",
                text_color="#4CAF50", font=ctk.CTkFont(size=12), wraplength=380, justify="left",
            ).grid(row=0, column=0, sticky="w", pady=2)
            return

        header = ctk.CTkLabel(
            self._scan_results, text=f"Content risk score: {score}/100 — {len(findings)} pattern(s) found",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#E57373",
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 6))

        for i, finding in enumerate(findings, start=1):
            text = f"[{finding.category.value}] \"{finding.matched_phrase}\" — {finding.explanation}"
            ctk.CTkLabel(
                self._scan_results, text=text, font=ctk.CTkFont(size=11),
                text_color="gray80", wraplength=380, justify="left",
            ).grid(row=i, column=0, sticky="w", pady=2)

    def _build_stat_cards(self) -> None:
        cards = [
            ("Emails Checked", "Total", ("gray20", "gray80")),
            ("High Risk", "High", ("#8B1E1E", "#F2B8B5")),
            ("Medium Risk", "Medium", ("#8A5A00", "#F5D89A")),
            ("Low Risk", "Low", ("#1E5C2E", "#B9E3C6")),
        ]
        for col, (title, key, colors) in enumerate(cards):
            card = ctk.CTkFrame(self, corner_radius=12)
            card.grid(row=1, column=col, sticky="nsew", padx=(0 if col == 0 else 10, 0))
            card.grid_columnconfigure(0, weight=1)

            title_label = ctk.CTkLabel(
                card, text=title, font=ctk.CTkFont(size=13), text_color="gray60"
            )
            title_label.grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")

            value_label = ctk.CTkLabel(
                card, text="0", font=ctk.CTkFont(size=32, weight="bold")
            )
            value_label.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

            self._stat_cards[key] = value_label

    def on_show(self) -> None:
        """Refresh stats from the database. Called every time this frame is raised."""
        try:
            counts = self.db.get_summary_counts()
        except Exception:
            logger.exception("Failed to load dashboard summary counts")
            counts = {"Total": 0, "High": 0, "Medium": 0, "Low": 0}

        for key, label in self._stat_cards.items():
            label.configure(text=str(counts.get(key, 0)))

        self._redraw_chart(counts)

    def _redraw_chart(self, counts: dict[str, int]) -> None:
        self._axis.clear()
        levels = ["High", "Medium", "Low"]
        values = [counts.get(level, 0) for level in levels]
        colors = ["#E57373", "#FFB74D", "#81C784"]

        if sum(values) == 0:
            self._axis.text(
                0.5, 0.5, "No analyses yet", ha="center", va="center",
                fontsize=11, color="gray",
            )
            self._axis.axis("off")
        else:
            self._axis.pie(
                values, labels=levels, colors=colors, autopct="%1.0f%%",
                textprops={"fontsize": 9},
            )
        self._chart_canvas.draw()
