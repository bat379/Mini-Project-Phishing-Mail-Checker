"""
Hacker Zone — a themed, just-for-fun tab.

Purely cosmetic/educational: a terminal-style "matrix rain" animation,
rotating cybersecurity trivia, and a "Spot the Phish" quiz game reusing
the safe, generic examples from education/phishing_examples.py.

Nothing here performs any real network, filesystem, or execution action —
it's an engagement feature, not a tool.
"""
from __future__ import annotations

import random
import string
import tkinter as tk

import customtkinter as ctk

from education.awareness_content import CYBER_FACTS
from education.phishing_examples import QUIZ_ITEMS
from utils.logger import get_logger

logger = get_logger(__name__)

TERMINAL_GREEN = "#39FF14"
TERMINAL_BG = "#0A0E0A"
MATRIX_CHARS = string.ascii_uppercase + string.digits

BANNER = r"""
 ____  _     _     _    ____                     _
|  _ \| |__ (_)___| |__/ ___| _   _  __ _ _ __ __| |
| |_) | '_ \| / __| '_ \___ \| | | |/ _` | '__/ _` |
|  __/| | | | \__ \ | | |__) | |_| | (_| | | | (_| |
|_|   |_| |_|_|___/_| |_|____/ \__,_|\__,_|_|  \__,_|

           >> H A C K E R   Z O N E <<
"""


class MatrixRain(tk.Canvas):
    """A small animated 'digital rain' canvas, purely decorative."""

    def __init__(self, master, width: int = 760, height: int = 140, **kwargs) -> None:
        super().__init__(
            master, width=width, height=height, bg=TERMINAL_BG, highlightthickness=0, **kwargs
        )
        self._width = width
        self._height = height
        self._font_size = 14
        self._columns = width // self._font_size
        self._drops = [random.randint(0, height // self._font_size) for _ in range(self._columns)]
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._tick()

    def stop(self) -> None:
        self._running = False

    def _tick(self) -> None:
        if not self._running:
            return
        self.delete("all")
        for col in range(self._columns):
            x = col * self._font_size
            y = self._drops[col] * self._font_size
            char = random.choice(MATRIX_CHARS)
            self.create_text(
                x, y, text=char, fill=TERMINAL_GREEN,
                font=("Courier", self._font_size, "bold"), anchor="nw",
            )
            if y > self._height and random.random() > 0.95:
                self._drops[col] = 0
            else:
                self._drops[col] += 1
        self.after(80, self._tick)


class HackerZoneFrame(ctk.CTkFrame):
    """Fun, terminal-themed easter-egg tab."""

    def __init__(self, master) -> None:
        super().__init__(master, fg_color=TERMINAL_BG, corner_radius=12)
        self.grid_columnconfigure(0, weight=1)

        self._quiz_index = 0
        self._quiz_score = 0
        self._quiz_answered = False

        self._build_banner()
        self._build_matrix_rain()
        self._build_fact_widget()
        self._build_quiz_widget()

    # ------------------------------------------------------------------ #
    def _build_banner(self) -> None:
        banner_label = ctk.CTkLabel(
            self,
            text=BANNER,
            font=ctk.CTkFont(family="Courier", size=12),
            text_color=TERMINAL_GREEN,
            justify="left",
        )
        banner_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")

        caption = ctk.CTkLabel(
            self,
            text="// purely educational — no real exploits, no real targets, all defense //",
            font=ctk.CTkFont(family="Courier", size=11),
            text_color="#7CFF7C",
        )
        caption.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

    def _build_matrix_rain(self) -> None:
        self.matrix = MatrixRain(self, width=760, height=120)
        self.matrix.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.matrix.start()

    def _build_fact_widget(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="#111811", corner_radius=10)
        frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame, text="[ FACT OF THE DAY ]",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            text_color=TERMINAL_GREEN,
        )
        title.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        self._fact_label = ctk.CTkLabel(
            frame, text=random.choice(CYBER_FACTS),
            font=ctk.CTkFont(family="Courier", size=12),
            text_color="#C8FFC8", wraplength=680, justify="left",
        )
        self._fact_label.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        next_btn = ctk.CTkButton(
            frame, text="next_fact()", fg_color="#1E3B1E", hover_color="#2E5C2E",
            text_color=TERMINAL_GREEN, font=ctk.CTkFont(family="Courier", size=12),
            command=self._show_next_fact,
        )
        next_btn.grid(row=2, column=0, padx=16, pady=(0, 12), sticky="w")

    def _show_next_fact(self) -> None:
        self._fact_label.configure(text=random.choice(CYBER_FACTS))

    def _build_quiz_widget(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="#111811", corner_radius=10)
        frame.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        self._quiz_frame = frame

        title = ctk.CTkLabel(
            frame, text="[ SPOT THE PHISH ]",
            font=ctk.CTkFont(family="Courier", size=13, weight="bold"),
            text_color=TERMINAL_GREEN,
        )
        title.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        self._quiz_email_label = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(family="Courier", size=12),
            text_color="#C8FFC8", wraplength=680, justify="left",
        )
        self._quiz_email_label.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, padx=16, pady=(0, 8), sticky="w")

        self._phish_btn = ctk.CTkButton(
            btn_row, text="🎣 Phishing", fg_color="#5C1E1E", hover_color="#7A2A2A",
            font=ctk.CTkFont(family="Courier", size=12),
            command=lambda: self._submit_quiz_answer(True),
        )
        self._phish_btn.grid(row=0, column=0, padx=(0, 8))

        self._legit_btn = ctk.CTkButton(
            btn_row, text="✅ Legitimate", fg_color="#1E5C2E", hover_color="#2A7A3A",
            font=ctk.CTkFont(family="Courier", size=12),
            command=lambda: self._submit_quiz_answer(False),
        )
        self._legit_btn.grid(row=0, column=1)

        self._quiz_feedback_label = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(family="Courier", size=12),
            text_color="#FFD866", wraplength=680, justify="left",
        )
        self._quiz_feedback_label.grid(row=3, column=0, padx=16, pady=(0, 4), sticky="w")

        self._quiz_score_label = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(family="Courier", size=12),
            text_color="#7CFF7C",
        )
        self._quiz_score_label.grid(row=4, column=0, padx=16, pady=(0, 12), sticky="w")

        self._load_quiz_item()

    def _load_quiz_item(self) -> None:
        self._quiz_answered = False
        item = QUIZ_ITEMS[self._quiz_index % len(QUIZ_ITEMS)]
        self._quiz_email_label.configure(
            text=f"From: {item.sender}\nSubject: {item.subject}"
        )
        self._quiz_feedback_label.configure(text="")
        self._update_score_label()

    def _submit_quiz_answer(self, guessed_phishing: bool) -> None:
        if self._quiz_answered:
            self._quiz_index += 1
            self._load_quiz_item()
            return

        item = QUIZ_ITEMS[self._quiz_index % len(QUIZ_ITEMS)]
        correct = guessed_phishing == item.is_phishing
        self._quiz_answered = True

        if correct:
            self._quiz_score += 1
            verdict = "✅ Correct!"
        else:
            verdict = "❌ Not quite."

        self._quiz_feedback_label.configure(
            text=f"{verdict} {item.explanation}\n(Click a button again to load the next one.)"
        )
        self._update_score_label()
        logger.debug("Quiz answered: correct=%s score=%s", correct, self._quiz_score)

    def _update_score_label(self) -> None:
        self._quiz_score_label.configure(
            text=f"score = {self._quiz_score} / {self._quiz_index + (1 if self._quiz_answered else 0)}"
        )

    def on_show(self) -> None:
        """Called by App.show_frame each time this tab is raised."""
        self.matrix.start()

    def on_hide(self) -> None:
        """Stop the animation loop when navigating away, to save CPU."""
        self.matrix.stop()
