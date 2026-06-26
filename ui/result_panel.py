"""Result panel for displaying algorithm execution logs with language support."""

from __future__ import annotations

from typing import List

import customtkinter as ctk

from .theme import COLORS, FONTS, SIZES, get_scaled_font
from .i18n import t, f


class ResultPanel(ctk.CTkFrame):
    """
    Scrollable log panel displaying step-by-step algorithm results
    with color-coded output.
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=SIZES["corner_radius"],
            **kwargs,
        )
        self._last_log: List[str] = []
        self._zoom_scale = 1.0
        self._build()

    def _build(self):
        # ── Header ──
        self._header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._header_frame.pack(fill="x", padx=16, pady=(16, 8))

        self._title_lbl = ctk.CTkLabel(
            self._header_frame,
            text=t("result_title"),
            font=FONTS["heading_sm"],
            text_color=COLORS["text_bright"],
            anchor="w",
        )
        self._title_lbl.pack(side="left")

        self._clear_btn = ctk.CTkButton(
            self._header_frame,
            text=t("clear_log"),
            font=FONTS["body_sm"],
            fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary_hover"],
            text_color=COLORS["text_secondary"],
            width=70,
            height=28,
            corner_radius=6,
            command=self.clear,
        )
        self._clear_btn.pack(side="right", padx=(10, 0))

        self._zoom_in_btn = ctk.CTkButton(
            self._header_frame, text="➕", width=28, height=28,
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["btn_secondary"], hover_color=COLORS["btn_secondary_hover"],
            corner_radius=SIZES["corner_radius_sm"],
            command=self._zoom_in
        )
        self._zoom_in_btn.pack(side="right", padx=2)

        self._zoom_out_btn = ctk.CTkButton(
            self._header_frame, text="➖", width=28, height=28,
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["btn_secondary"], hover_color=COLORS["btn_secondary_hover"],
            corner_radius=SIZES["corner_radius_sm"],
            command=self._zoom_out
        )
        self._zoom_out_btn.pack(side="right", padx=2)

        # ── Log Text ──
        self._textbox = ctk.CTkTextbox(
            self,
            font=FONTS["log_text"],
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["text_primary"],
            corner_radius=SIZES["corner_radius_sm"],
            scrollbar_button_color=COLORS["bg_card"],
            scrollbar_button_hover_color=COLORS["accent_primary"],
            wrap="word",
            activate_scrollbars=True,
        )
        self._textbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Configure text tags for coloring
        self._textbox.tag_config("success", foreground=COLORS["success"])
        self._textbox.tag_config("warning", foreground=COLORS["warning"])
        self._textbox.tag_config("danger", foreground=COLORS["danger"])
        self._textbox.tag_config("info", foreground=COLORS["info"])
        self._textbox.tag_config("accent", foreground=COLORS["accent_primary"])
        self._textbox.tag_config("header", foreground=COLORS["text_bright"])

        # Welcome message
        self._show_welcome()

    def _show_welcome(self):
        """Show initial welcome message."""
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.insert("end", "  " + t("welcome_1") + "\n\n", "info")
        self._textbox.insert("end", "  " + t("welcome_2") + "\n", "accent")
        self._textbox.insert("end", "  " + t("welcome_3") + "\n", "accent")
        self._textbox.insert("end", "  " + t("welcome_4") + "\n", "accent")
        self._textbox.configure(state="disabled")

    def display_log(self, log_lines: List[str]):
        """Display algorithm execution log with color coding."""
        self._last_log = log_lines
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")

        for line in log_lines:
            tag = self._detect_tag(line)
            # Apply reshaping for Persian rendering correctness
            reshaped_line = f(line)
            self._textbox.insert("end", reshaped_line + "\n", tag)

        self._textbox.configure(state="disabled")
        self._textbox.see("end")

    def append_log(self, line: str):
        """Append a single line to the log."""
        self._last_log.append(line)
        self._textbox.configure(state="normal")
        tag = self._detect_tag(line)
        reshaped_line = f(line)
        self._textbox.insert("end", reshaped_line + "\n", tag)
        self._textbox.configure(state="disabled")
        self._textbox.see("end")

    def _detect_tag(self, line: str) -> str:
        """Detect appropriate color tag based on line content."""
        stripped = line.strip()
        if "✅" in stripped or "🟢" in stripped or "Success" in stripped or "safe" in stripped or "resolved" in stripped:
            return "success"
        elif "⚠️" in stripped or "🟡" in stripped or "⏳" in stripped or "warning" in stripped or "denied" in stripped or "waiting" in stripped:
            return "warning"
        elif "❌" in stripped or "🔴" in stripped or "🗑️" in stripped or "terminated" in stripped or "Deadlock" in stripped:
            return "danger"
        elif "🔍" in stripped or "🛡️" in stripped or "📊" in stripped or "Strategy" in stripped:
            return "header"
        elif "ℹ️" in stripped or stripped.startswith("   →") or "Initial" in stripped:
            return "info"
        elif stripped.startswith("   مرحله") or stripped.startswith("   Step") or stripped.startswith("   Checking"):
            return "accent"
        return ""

    def clear(self):
        """Clear the log."""
        self._last_log = []
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")

    def _zoom_in(self):
        new_scale = round(max(0.7, min(self._zoom_scale + 0.1, 1.7)), 1)
        if new_scale != self._zoom_scale:
            self._zoom_scale = new_scale
            self._apply_zoom()

    def _zoom_out(self):
        new_scale = round(max(0.7, min(self._zoom_scale - 0.1, 1.7)), 1)
        if new_scale != self._zoom_scale:
            self._zoom_scale = new_scale
            self._apply_zoom()

    def _apply_zoom(self):
        self._textbox.configure(font=get_scaled_font("log_text", self._zoom_scale))

    def refresh_translation(self):
        """Refresh panel titles and logs representation."""
        self._title_lbl.configure(text=t("result_title"))
        self._clear_btn.configure(text=t("clear_log"))
        if not self._last_log:
            self._show_welcome()
        else:
            self.display_log(self._last_log)
